from __future__ import annotations

__all__ = [
    "bubble_sort",
    "merge_sort",
    "quick_sort",
    "linear_search",
    "binary_search",
    "bfs",
    "dfs",
    "dijkstra",
    "__version__",
]

__version__ = "0.1.1"

from .algorithms.sorting import bubble_sort, merge_sort, quick_sort  # noqa: E402
from .algorithms.searching import binary_search, linear_search  # noqa: E402
from .algorithms.graphs import bfs, dfs, dijkstra  # noqa: E402
