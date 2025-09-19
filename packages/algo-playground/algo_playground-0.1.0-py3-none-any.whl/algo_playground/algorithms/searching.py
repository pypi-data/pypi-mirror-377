from __future__ import annotations

from typing import Iterable, Sequence


def linear_search(data: Iterable[int], target: int | None) -> int:
    """
    Linear search for target. Returns index or -1 if not found.
    """
    if target is None:
        return -1
    for idx, value in enumerate(data):
        if value == target:
            return idx
    return -1


def binary_search(data: Sequence[int], target: int | None) -> int:
    """
    Binary search over a sorted sequence. Returns index or -1 if not found.
    """
    if target is None:
        return -1
    low = 0
    high = len(data) - 1
    while low <= high:
        mid = (low + high) // 2
        if data[mid] == target:
            return mid
        if data[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
