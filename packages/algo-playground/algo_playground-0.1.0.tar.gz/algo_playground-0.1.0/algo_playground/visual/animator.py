from __future__ import annotations

import time
import math
from typing import Callable, Iterable, List, Sequence

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..algorithms.sorting import SortStep

console = Console()


def _sleep(delay_seconds: float) -> None:
    if delay_seconds > 0:
        time.sleep(delay_seconds)


def _scale_values(values: Sequence[int], max_bar: int = 12) -> List[int]:
    if not values:
        return []
    max_val = max(values)
    if max_val <= 0:
        return [1 for _ in values]
    return [max(1, int(v / max_val * max_bar)) for v in values]


def _render_array_table(
    values: Sequence[int],
    compare: set[int] | None = None,
    swap: set[int] | None = None,
    title: str | None = None,
    subtitle: str | None = None,
) -> Panel:
    compare = compare or set()
    swap = swap or set()

    idx_row = Table.grid(expand=True)
    for i in range(len(values)):
        idx_row.add_column(justify="center")
    if values:
        idx_row.add_row(*[Text(str(i), style="dim") for i in range(len(values))])

    bars_row = Table.grid(expand=True)
    for i in range(len(values)):
        bars_row.add_column(justify="center")

    scaled = _scale_values(values)
    cells: List[Text] = []
    for i, (v, h) in enumerate(zip(values, scaled)):
        bar = "█" * h
        if i in swap:
            style = "bold white on red"
        elif i in compare:
            style = "black on yellow"
        else:
            style = "white on blue"
        cell = Text(bar + f"\n{v}", style=style, justify="center")
        cells.append(cell)
    if cells:
        bars_row.add_row(*cells)

    grid = Table.grid(padding=(0, 1))
    if values:
        grid.add_row(idx_row)
    grid.add_row(bars_row)

    legend = Text()
    legend.append("Legend: ")
    legend.append("compare", style="black on yellow")
    legend.append("  ")
    legend.append("swap", style="bold white on red")
    legend.append("  ")
    legend.append("normal", style="white on blue")

    content = Group(grid, Text(), legend)
    panel_title = title or "Array"
    return Panel(content, title=panel_title, subtitle=subtitle, subtitle_align="left")


def animate_sorting(
    algo: Callable[..., tuple[list[int], int]],
    data: Iterable[int],
    delay_seconds: float = 0.02,
) -> None:
    """
    Animate a sorting algorithm that supports trace via on_step callback.
    Shows a colored bar chart, indices, and step counters.
    """
    working = list(data)
    step_counter = 0
    last_compare: set[int] = set()
    last_swap: set[int] = set()
    comparisons_total = 0

    def build_render(status: str) -> Panel:
        header = f"Steps: {step_counter} | Status: {status}"
        return _render_array_table(working, last_compare, last_swap, title="Sorting", subtitle=header)

    with Live(build_render("Starting"), refresh_per_second=30, console=console) as live:
        def on_step(step: SortStep) -> None:
            nonlocal step_counter, working, last_compare, last_swap
            step_counter += 1
            working = list(step.array)
            last_compare = set(step.compare_indices or [])
            last_swap = set(step.swap_indices or [])
            live.update(build_render("Working"))
            _sleep(delay_seconds)

        sorted_arr, comparisons = algo(working, trace=True, on_step=on_step)
        comparisons_total = comparisons
        working[:] = sorted_arr
        last_compare.clear()
        last_swap.clear()
        live.update(build_render(f"Done | Comparisons: {comparisons_total}"))
        _sleep(max(0.3, delay_seconds))

    console.print(Panel.fit(f"Sorted: {working}", title="Result"))


def _draw_graph_panel(graph: dict[str, list[str]], width: int = 64, height: int = 22) -> Panel:
    """
    Draw a simple ASCII circular-layout graph with minimal-overlap edges.
    Nodes are placed around a circle with numeric labels, and each edge is a single
    arrow glyph near the source pointing toward the neighbor's direction.
    A legend maps numeric labels to node names below the drawing.
    """
    nodes = list(graph.keys())
    if not nodes:
        return Panel(Text("<empty graph>"), title="Graph Drawing")

    # Canvas
    w, h = max(20, width), max(10, height)
    canvas = [[" " for _ in range(w)] for _ in range(h)]

    # Node positions on a circle
    cx, cy = w // 2, h // 2
    radius = int(min(w, h) * 0.35)
    pos: dict[str, tuple[int, int]] = {}
    label_map: dict[str, str] = {}
    for idx, node in enumerate(nodes):
        ang = 2 * math.pi * idx / max(1, len(nodes))
        x = cx + int(radius * math.cos(ang))
        y = cy + int(radius * math.sin(ang))
        pos[node] = (x, y)
        label_map[node] = str(idx)

    # Place node labels first
    for node, (x, y) in pos.items():
        label = label_map[node]
        for i, ch in enumerate(label):
            xx = x + i
            if 0 <= xx < w and 0 <= y < h:
                canvas[y][xx] = ch

    # Draw a single arrow just outside the node toward neighbor direction
    def arrow_for(dx: float, dy: float) -> str:
        ang = math.atan2(dy, dx)
        deg = (math.degrees(ang) + 360) % 360
        # 8-direction arrows
        if 337.5 <= deg or deg < 22.5:
            return "→"
        if 22.5 <= deg < 67.5:
            return "↗"
        if 67.5 <= deg < 112.5:
            return "↑"
        if 112.5 <= deg < 157.5:
            return "↖"
        if 157.5 <= deg < 202.5:
            return "←"
        if 202.5 <= deg < 247.5:
            return "↙"
        if 247.5 <= deg < 292.5:
            return "↓"
        return "↘"

    occupied = {(x, y) for x in range(w) for y in range(h) if canvas[y][x] != " "}

    for u, nbrs in graph.items():
        x0, y0 = pos[u]
        for v in nbrs:
            if v not in pos:
                continue
            x1, y1 = pos[v]
            dx, dy = x1 - x0, y1 - y0
            # Place arrow one step away from node center in the direction of v
            step = max(1, int(radius * 0.2))
            dist = max(1.0, math.hypot(dx, dy))
            ax = x0 + int(round(dx / dist * step))
            ay = y0 + int(round(dy / dist * step))
            # If occupied, try a few offsets around
            candidates = [
                (ax, ay),
                (ax + 1, ay), (ax - 1, ay),
                (ax, ay + 1), (ax, ay - 1),
                (ax + 1, ay + 1), (ax - 1, ay - 1),
                (ax + 1, ay - 1), (ax - 1, ay + 1),
            ]
            arrow = arrow_for(dx, dy)
            for px, py in candidates:
                if 0 <= px < w and 0 <= py < h and (px, py) not in occupied:
                    canvas[py][px] = arrow
                    occupied.add((px, py))
                    break

    lines = ["".join(row) for row in canvas]
    drawing = Text("\n".join(lines), style="cyan")

    # Legend mapping numbers to node labels
    legend_table = Table.grid(expand=True)
    legend_table.add_column(justify="left")
    pairs: List[str] = []
    for node in nodes:
        pairs.append(f"{label_map[node]}: {node}")
    # split into two columns if many
    left = pairs[::2]
    right = pairs[1::2]
    if right:
        legend = Table.grid()
        legend.add_column()
        legend.add_column()
        legend.add_row(Text("\n".join(left)), Text("\n".join(right)))
    else:
        legend = Text("\n".join(left))

    help_text = Text("Arrows indicate direction of edges from each node.", style="dim")
    return Panel(Group(drawing, Text(), legend, Text(), help_text), title="Graph Overview")


def animate_binary_search(
    data: Sequence[int],
    target: int | None,
    is_binary: bool = True,
    delay_seconds: float = 0.02,
) -> None:
    """
    Animate linear or binary search over an array with step-by-step printed states.
    Prints a row per step with pointers and highlights, so beginners can follow along
    even if the terminal doesn't fully support Live updates.
    """
    arr = list(data)
    target = -1 if target is None else target

    def print_state(lo: int | None, mid: int | None, hi: int | None, note: str) -> None:
        compare: set[int] = set()
        if mid is not None:
            compare.add(mid)
        panel = _render_array_table(arr, compare=compare, swap=set(), title=("Binary Search" if is_binary else "Linear Search"), subtitle=note)
        console.print(panel)

    if not arr:
        console.print("[]")
        return

    if is_binary:
        lo, hi = 0, len(arr) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            print_state(lo, mid, hi, f"lo={lo} mid={mid} hi={hi} target={target}")
            _sleep(delay_seconds)
            if arr[mid] == target:
                print_state(lo, mid, hi, f"Found at {mid}")
                _sleep(max(0.2, delay_seconds))
                return
            if arr[mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        console.print(f"[bold red]{target} not found[/bold red]")
    else:
        for i, v in enumerate(arr):
            print_state(None, i, None, f"i={i} target={target}")
            _sleep(delay_seconds)
            if v == target:
                print_state(None, i, None, f"Found at {i}")
                _sleep(max(0.2, delay_seconds))
                return
        console.print(f"[bold red]{target} not found[/bold red]")


def animate_graph_traversal(
    graph: dict[str, list[str]],
    order: list[str],
    delay_seconds: float = 0.02,
) -> None:
    """
    Simple textual animation for graph traversal order with adjacency list and visited set.
    Now also shows a pre-traversal ASCII graph drawing.
    """
    # Pre-traversal drawing
    console.print(_draw_graph_panel(graph))
    _sleep(max(delay_seconds * 2, 0.2))

    visited: set[str] = set()

    def render(current: str | None) -> Panel:
        table = Table(title="Graph (Adjacency List)", show_lines=True, expand=True)
        table.add_column("Node", style="bold cyan", no_wrap=True)
        table.add_column("Neighbors", style="white")
        for node, neighbors in graph.items():
            style = "bold green" if node in visited else ("bold yellow" if node == current else "white")
            nbrs = ", ".join(neighbors)
            table.add_row(Text(node, style=style), Text(nbrs, style="dim"))
        footer = Text(f"Visited: {list(visited)}")
        return Panel(Group(table, Text(), footer))

    with Live(render(None), refresh_per_second=30, console=console) as live:
        for node in order:
            visited.add(node)
            live.update(render(node))
            _sleep(delay_seconds)
        _sleep(max(0.3, delay_seconds))
    console.print("[bold green]Traversal complete[/bold green]")
