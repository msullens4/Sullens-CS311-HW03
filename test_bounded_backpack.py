"""
Homework 3: The Bounded Backpack -- verification suite.

Run: python test_bounded_backpack.py
Prints the Success Token only if every check below passes.
"""

import base64
import hashlib
import random
import sys
import threading
import time

from bounded_backpack import BackpackTimeoutError, BoundedBackpack

ASSIGNMENT_ID = "HW03"


def get_student_id() -> str:
    """Prompt for the student's USI username; baked into the Success Token
    so a copied/shared token decodes to someone else's name, not yours."""
    student_id = input("Enter your USI username (e.g. cwill): ").strip()
    while not student_id:
        student_id = input("Username cannot be blank. Enter your USI username: ").strip()
    return student_id


def generate_token(assignment_id: str, student_id: str) -> str:
    digest = hashlib.sha256(f"CS311-{assignment_id}-{student_id}-VERIFIED".encode()).hexdigest()[:16]
    raw = f"CS311|{assignment_id}|{student_id}|PASS|{digest}"
    return base64.b64encode(raw.encode()).decode()


def print_success_banner(assignment_id: str) -> None:
    student_id = get_student_id()
    token = generate_token(assignment_id, student_id)
    print("\n" + "=" * 60)
    print(f"  ALL CHECKS PASSED -- {assignment_id}")
    print(f"  STUDENT: {student_id}")
    print("  SUCCESS TOKEN (paste this into Blackboard):")
    print(f"  {token}")
    print("=" * 60 + "\n")


def check(label: str, condition: bool, failures: list) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}")
    if not condition:
        failures.append(label)


def basic_correctness(failures: list) -> None:
    bp = BoundedBackpack(capacity=3)
    bp.push("a")
    bp.push("b")
    check("push then pop returns LIFO order (b, then a)", bp.pop() == "b", failures)
    check("second pop returns the first-pushed item (a)", bp.pop() == "a", failures)
    check("backpack length is 0 after draining", len(bp) == 0, failures)


def blocking_push_test(failures: list) -> None:
    bp = BoundedBackpack(capacity=2)
    bp.push("x")
    bp.push("y")  # now full

    result = {}

    def blocked_pusher():
        bp.push("z", timeout=5.0)
        result["done"] = True

    t = threading.Thread(target=blocked_pusher)
    start = time.time()
    t.start()
    time.sleep(0.3)
    check("push() on a full backpack is still blocked after 0.3s", "done" not in result, failures)

    bp.pop()  # frees a slot -> should wake the blocked pusher
    t.join(timeout=2.0)
    elapsed = time.time() - start
    check("push() unblocks and completes once space frees up", result.get("done") is True, failures)
    check("push() didn't take unreasonably long to unblock (< 2s)", elapsed < 2.0, failures)


def blocking_pop_test(failures: list) -> None:
    bp = BoundedBackpack(capacity=2)
    result = {}

    def blocked_popper():
        result["value"] = bp.pop(timeout=5.0)

    t = threading.Thread(target=blocked_popper)
    start = time.time()
    t.start()
    time.sleep(0.3)
    check("pop() on an empty backpack is still blocked after 0.3s", "value" not in result, failures)

    bp.push("arrived")
    t.join(timeout=2.0)
    elapsed = time.time() - start
    check("pop() unblocks and returns the item once one arrives", result.get("value") == "arrived", failures)
    check("pop() didn't take unreasonably long to unblock (< 2s)", elapsed < 2.0, failures)


def timeout_test(failures: list) -> None:
    bp = BoundedBackpack(capacity=2)
    start = time.time()
    try:
        bp.pop(timeout=0.3)
        check("pop() on a permanently empty backpack raises BackpackTimeoutError", False, failures)
    except BackpackTimeoutError:
        elapsed = time.time() - start
        check("pop() raises BackpackTimeoutError", True, failures)
        check("pop() timeout fires close to the requested duration (0.2s-1.0s)", 0.2 <= elapsed <= 1.0, failures)

    bp2 = BoundedBackpack(capacity=1)
    bp2.push("full")
    try:
        bp2.push("overflow", timeout=0.3)
        check("push() on a permanently full backpack raises BackpackTimeoutError", False, failures)
    except BackpackTimeoutError:
        check("push() raises BackpackTimeoutError", True, failures)


def concurrency_stress_test(failures: list, num_producers: int = 20, num_consumers: int = 10, items_per_producer: int = 25) -> None:
    bp = BoundedBackpack(capacity=15)
    total_items = num_producers * items_per_producer
    consumed = []
    consumed_lock = threading.Lock()
    crash_flags = []

    def producer(pid: int) -> None:
        try:
            for i in range(items_per_producer):
                bp.push((pid, i), timeout=10.0)
        except Exception:
            crash_flags.append(True)

    def consumer() -> None:
        try:
            while True:
                with consumed_lock:
                    if len(consumed) >= total_items:
                        return
                try:
                    item = bp.pop(timeout=0.5)
                except BackpackTimeoutError:
                    with consumed_lock:
                        if len(consumed) >= total_items:
                            return
                    continue
                with consumed_lock:
                    consumed.append(item)
        except Exception:
            crash_flags.append(True)

    producers = [threading.Thread(target=producer, args=(i,)) for i in range(num_producers)]
    consumers = [threading.Thread(target=consumer) for _ in range(num_consumers)]
    for t in consumers + producers:
        t.start()
    for t in producers:
        t.join()
    for t in consumers:
        t.join(timeout=15.0)

    check("concurrency stress test: no thread raised an exception", not crash_flags, failures)
    check(f"concurrency stress test: all {total_items} items consumed exactly once", len(consumed) == total_items and len(set(consumed)) == total_items, failures)
    check("backpack never exceeded its capacity (no observed overflow in the final state)", len(bp) <= bp.capacity, failures)


def main() -> int:
    failures: list = []

    print("Running basic correctness checks...\n")
    basic_correctness(failures)
    if failures:
        print(f"\n{len(failures)} check(s) failed. No token issued.")
        return 1

    print("\nTesting that push() blocks when full...\n")
    blocking_push_test(failures)

    print("\nTesting that pop() blocks when empty...\n")
    blocking_pop_test(failures)

    print("\nTesting timeouts...\n")
    timeout_test(failures)

    if failures:
        print(f"\n{len(failures)} check(s) failed. No token issued.")
        return 1

    print("\nRunning concurrency stress test (20 producers x 10 consumers)...\n")
    concurrency_stress_test(failures)

    print()
    if failures:
        print(f"{len(failures)} check(s) failed. No token issued.")
        return 1

    print_success_banner(ASSIGNMENT_ID)
    return 0


if __name__ == "__main__":
    sys.exit(main())
