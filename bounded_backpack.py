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
        raise NotImplementedError

    def pop(self, timeout: Optional[float] = None) -> Any:
        """
        Block while the backpack is empty, waiting until an item is
        available (or `timeout` seconds elapse -> BackpackTimeoutError).
        Remove and return the top item, then wake any thread waiting in push().
        """
        # TODO
        raise NotImplementedError
