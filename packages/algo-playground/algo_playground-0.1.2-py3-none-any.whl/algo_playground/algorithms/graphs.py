from __future__ import annotations

from collections import deque
from typing import Deque, Dict, Iterable, List, Mapping
import random


def generate_random_graph(
    rng: random.Random,
    num_nodes: int,
    edge_factor: int = 2,
    weighted: bool = False,
) -> Dict[str, list] | Dict[str, list[tuple[str, int]]]:
    """
    Generate a random directed graph with node labels 'N0'...'N{num_nodes-1}'.
    If weighted=True, edges carry positive integer weights in [1, 9].
    """
    nodes = [f"N{i}" for i in range(num_nodes)]
    graph: Dict[str, list] = {n: [] for n in nodes}
    for src in nodes:
        degree = rng.randint(1, max(1, edge_factor))
        targets = rng.sample(nodes, k=min(degree, num_nodes))
        for dst in targets:
            if dst == src:
                continue
            if weighted:
                graph[src].append((dst, rng.randint(1, 9)))
            else:
                graph[src].append(dst)
    return graph


def bfs(graph: Mapping[str, Iterable[str]], start: str) -> List[str]:
    """
    Breadth-first traversal. Returns order of visited nodes.
    """
    visited: set[str] = set()
    order: List[str] = []
    queue: Deque[str] = deque([start])
    visited.add(start)
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order


def dfs(graph: Mapping[str, Iterable[str]], start: str) -> List[str]:
    """
    Depth-first traversal (iterative). Returns order of visited nodes.
    """
    visited: set[str] = set()
    order: List[str] = []
    stack: List[str] = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        neighbors = list(graph.get(node, []))
        neighbors.reverse()
        for neighbor in neighbors:
            if neighbor not in visited:
                stack.append(neighbor)
    return order


def dijkstra(graph: Mapping[str, Iterable[tuple[str, int]]], start: str) -> Dict[str, int]:
    """
    Dijkstra single-source shortest paths (non-negative weights).
    Returns distances mapping.
    """
    import heapq

    distances: Dict[str, int] = {start: 0}
    pq: list[tuple[int, str]] = [(0, start)]
    visited: set[str] = set()
    while pq:
        d, node = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)
        for neighbor, weight in graph.get(node, []):
            nd = d + int(weight)
            if neighbor not in distances or nd < distances[neighbor]:
                distances[neighbor] = nd
                heapq.heappush(pq, (nd, neighbor))
    return distances
