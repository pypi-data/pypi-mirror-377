from __future__ import annotations

from algo_playground.algorithms.searching import binary_search, linear_search


def test_linear_search_found_and_not_found() -> None:
    arr = [1, 3, 5, 7, 9]
    assert linear_search(arr, 7) == 3
    assert linear_search(arr, 2) == -1
    assert linear_search(arr, None) == -1


def test_binary_search_basic() -> None:
    arr = [1, 3, 5, 7, 9]
    assert binary_search(arr, 1) == 0
    assert binary_search(arr, 9) == 4
    assert binary_search(arr, 4) == -1
    assert binary_search(arr, None) == -1
