# Homework 3: The Bounded Backpack

Public template: https://github.com/cwillpinto/cs311-hw03-bounded-backpack

Full assignment: `HW3_The_Bounded_Backpack.md`.

## Run
```bash
python test_bounded_backpack.py
```
Complete `bounded_backpack.py` using a `threading.Condition` (not a
bare `Lock`). The script checks LIFO correctness, confirms `push()`
actually blocks when full and `pop()` actually blocks when empty
(and unblocks correctly once space/an item appears), checks timeouts
raise `BackpackTimeoutError`, then runs a concurrency stress test.
Success Token prints once every check passes.

## Submit
1. `HW3_Theory.pdf` (or `.md`)
2. `bounded_backpack.py`
3. The Success Token
