"""
Homework 3: The Bounded Backpack -- starter.

Complete BoundedBackpack below. See HW3_The_Bounded_Backpack.md,
Part B, for the full requirements.
"""

import threading
import time
from typing import Any, List, Optional


class BackpackTimeoutError(Exception):
    """Raised when push()/pop() waits longer than its timeout without success."""


class BoundedBackpack:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self._items: List[Any] = []
        self._condition = threading.Condition()

    def __len__(self) -> int:
        with self._condition:
            return len(self._items)

    def push(self, item: Any, timeout: Optional[float] = None) -> None:
        """
        Block while the backpack is full, waiting until space is
        available (or `timeout` seconds elapse -> BackpackTimeoutError).
        Insert at the top (LIFO), then wake any thread waiting in pop().
        """
        # TODO
        with self._condition:
            start_time = time.monotonic()

            while len(self._items) >= self.capacity:
                if timeout is None:
                    self._condition.wait()

                else:
                    elapsed = time.monotonic() - start_time
                    remaining = timeout - elapsed

                    if remaining <= 0:
                        raise BackpackTimeoutError(
                            "push() timed out waiting for space"
                        )

                    self._condition.wait(remaining)

            self._items.append(item)
            self._condition.notify()

    def pop(self, timeout: Optional[float] = None) -> Any:
        """
        Block while the backpack is empty, waiting until an item is
        available (or `timeout` seconds elapse -> BackpackTimeoutError).
        Remove and return the top item, then wake any thread waiting in push().
        """
        # TODO
        with self._condition:
            start_time = time.monotonic()

            while not self._items:
                if timeout is None:
                    self._condition.wait()

                else:
                    elapsed = time.monotonic() - start_time
                    remaining = timeout - elapsed

                    if remaining <= 0:
                        raise BackpackTimeoutError(
                            "pop() timed out waiting for an item"
                        )

                    self._condition.wait(remaining)

            item = self._items.pop()
            self._condition.notify()

            return item
