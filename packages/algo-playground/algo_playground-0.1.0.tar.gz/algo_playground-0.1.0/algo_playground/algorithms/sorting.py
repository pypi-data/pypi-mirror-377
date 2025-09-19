from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Tuple


@dataclass(frozen=True)
class SortStep:
    array: Tuple[int, ...]
    compare_indices: Tuple[int, int] | None = None
    swap_indices: Tuple[int, int] | None = None


TraceCallback = Callable[[SortStep], None]


def bubble_sort(data: Iterable[int], trace: bool = False, on_step: TraceCallback | None = None) -> Tuple[List[int], int]:
    """
    Bubble sort. Returns (sorted_list, comparisons_count).
    If trace=True, calls on_step with SortStep for comparisons and swaps.
    """
    arr = list(data)
    n = len(arr)
    comparisons = 0
    for i in range(n):
        for j in range(0, n - i - 1):
            comparisons += 1
            if trace and on_step is not None:
                on_step(SortStep(tuple(arr), compare_indices=(j, j + 1)))
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                if trace and on_step is not None:
                    on_step(SortStep(tuple(arr), swap_indices=(j, j + 1)))
    return arr, comparisons


def merge_sort(data: Iterable[int], trace: bool = False, on_step: TraceCallback | None = None) -> Tuple[List[int], int]:
    """
    Merge sort. Returns (sorted_list, comparisons_count).
    Emits steps for merges if trace=True.
    """
    arr = list(data)
    comparisons = 0

    def merge(left: List[int], right: List[int]) -> List[int]:
        nonlocal comparisons
        result: List[int] = []
        i = j = 0
        while i < len(left) and j < len(right):
            comparisons += 1
            if trace and on_step is not None:
                on_step(SortStep(tuple(left + right), compare_indices=(i, len(left) + j)))
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def sort(lst: List[int]) -> List[int]:
        if len(lst) <= 1:
            return lst
        mid = len(lst) // 2
        left = sort(lst[:mid])
        right = sort(lst[mid:])
        merged = merge(left, right)
        if trace and on_step is not None:
            on_step(SortStep(tuple(merged)))
        return merged

    return sort(arr), comparisons


def quick_sort(data: Iterable[int], trace: bool = False, on_step: TraceCallback | None = None) -> Tuple[List[int], int]:
    """
    Quick sort (Lomuto partition). Returns (sorted_list, comparisons_count).
    Emits steps for comparisons and swaps if trace=True.
    """
    arr = list(data)
    comparisons = 0

    def _quick(low: int, high: int) -> None:
        nonlocal comparisons
        if low >= high:
            return
        pivot = arr[high]
        i = low
        for j in range(low, high):
            comparisons += 1
            if trace and on_step is not None:
                on_step(SortStep(tuple(arr), compare_indices=(j, high)))
            if arr[j] <= pivot:
                arr[i], arr[j] = arr[j], arr[i]
                if trace and on_step is not None:
                    on_step(SortStep(tuple(arr), swap_indices=(i, j)))
                i += 1
        arr[i], arr[high] = arr[high], arr[i]
        if trace and on_step is not None:
            on_step(SortStep(tuple(arr), swap_indices=(i, high)))
        _quick(low, i - 1)
        _quick(i + 1, high)

    _quick(0, len(arr) - 1)
    return arr, comparisons
