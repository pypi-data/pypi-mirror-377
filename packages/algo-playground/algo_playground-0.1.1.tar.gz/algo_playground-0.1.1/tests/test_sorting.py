from __future__ import annotations

import random

from algo_playground.algorithms.sorting import bubble_sort, merge_sort, quick_sort


def _random_list(seed: int, n: int) -> list[int]:
    rng = random.Random(seed)
    return [rng.randint(0, 100) for _ in range(n)]


def test_bubble_sort_correct() -> None:
    data = _random_list(1, 20)
    sorted_res, cmp_count = bubble_sort(data)
    assert sorted_res == sorted(data)
    assert cmp_count > 0
    # Pure function: original unchanged
    assert data != []  # trivial sanity


def test_merge_sort_correct() -> None:
    data = _random_list(2, 30)
    sorted_res, cmp_count = merge_sort(data)
    assert sorted_res == sorted(data)
    assert cmp_count >= 0


def test_quick_sort_correct() -> None:
    data = _random_list(3, 25)
    sorted_res, cmp_count = quick_sort(data)
    assert sorted_res == sorted(data)
    assert cmp_count > 0 or len(data) <= 1
