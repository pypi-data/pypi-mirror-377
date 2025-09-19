from __future__ import annotations

from algo_playground.algorithms.graphs import bfs, dfs, dijkstra


def test_bfs_and_dfs_order() -> None:
    graph = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["D"],
        "D": [],
    }
    assert bfs(graph, "A") == ["A", "B", "C", "D"]
    # DFS order depends on push order; My implementation reverses neighbors into stack
    assert dfs(graph, "A") == ["A", "B", "D", "C"]


def test_dijkstra_distances() -> None:
    graph_w = {
        "A": [("B", 2), ("C", 5)],
        "B": [("C", 1), ("D", 4)],
        "C": [("D", 1)],
        "D": [],
    }
    dist = dijkstra(graph_w, "A")
    assert dist["A"] == 0
    assert dist["B"] == 2
    assert dist["C"] == 3
    assert dist["D"] == 4
