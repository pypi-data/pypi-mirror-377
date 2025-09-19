from __future__ import annotations

import random
import time
from typing import List

import click
from rich.console import Console
from rich.table import Table

from .algorithms.graphs import bfs, dijkstra, dfs, generate_random_graph
from .algorithms.searching import binary_search, linear_search
from .algorithms.sorting import bubble_sort, merge_sort, quick_sort
from .visual import animator as viz

console = Console()

ALGO_CATEGORIES = {
    "sorting": ["bubble_sort", "merge_sort", "quick_sort"],
    "searching": ["linear_search", "binary_search"],
    "graphs": ["bfs", "dfs", "dijkstra"],
}


def _safe_call(func_name: str, *args, **kwargs) -> bool:
    func = getattr(viz, func_name, None)
    if callable(func):
        func(*args, **kwargs)
        return True
    return False


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(package_name="algo-playground")
def cli() -> None:
    """algo-playground: explore algorithms in your terminal."""


@cli.command("list")
def list_algorithms() -> None:
    """List available algorithms by category."""
    table = Table(title="Available Algorithms")
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Algorithms", style="green")
    for category, names in ALGO_CATEGORIES.items():
        table.add_row(category, ", ".join(names))
    console.print(table)


@cli.command("run")
@click.argument("algorithm", type=str)
@click.option("--size", type=int, default=20, show_default=True, help="Dataset size.")
@click.option(
    "--speed",
    type=float,
    default=0.02,
    show_default=True,
    help="Seconds per visual step.",
)
@click.option("--visual", is_flag=True, help="Enable step-by-step visualization.")
@click.option("--seed", type=int, default=None, help="Random seed for reproducibility.")
@click.option(
    "--target",
    type=int,
    default=None,
    help="Target value for searching algorithms (auto-chosen if omitted).",
)
def run_algorithm(
    algorithm: str,
    size: int,
    speed: float,
    visual: bool,
    seed: int | None,
    target: int | None,
) -> None:
    """Run an algorithm by name with options."""
    algorithm = algorithm.strip().lower()
    rng = random.Random(seed)
    t0 = time.perf_counter()

    if algorithm in {"bubble_sort", "merge_sort", "quick_sort"}:
        data = [rng.randint(0, 99) for _ in range(max(size, 0))]
        console.print(f"[bold]Input:[/bold] {data}")
        if visual:
            called = False
            if algorithm == "bubble_sort":
                called = _safe_call("animate_sorting", bubble_sort, data, delay_seconds=speed)
            elif algorithm == "merge_sort":
                called = _safe_call("animate_sorting", merge_sort, data, delay_seconds=speed)
            else:
                called = _safe_call("animate_sorting", quick_sort, data, delay_seconds=speed)
            if not called:
                # Fallback non-visual
                if algorithm == "bubble_sort":
                    result, _ = bubble_sort(data, trace=False)
                elif algorithm == "merge_sort":
                    result, _ = merge_sort(data, trace=False)
                else:
                    result, _ = quick_sort(data, trace=False)
                console.print(f"[bold green]Sorted:[/bold green] {result}")
        else:
            if algorithm == "bubble_sort":
                result, _ = bubble_sort(data, trace=False)
            elif algorithm == "merge_sort":
                result, _ = merge_sort(data, trace=False)
            else:
                result, _ = quick_sort(data, trace=False)
            console.print(f"[bold green]Sorted:[/bold green] {result}")

    elif algorithm in {"linear_search", "binary_search"}:
        data = sorted([rng.randint(0, 99) for _ in range(max(size, 0))])
        if target is None and data:
            target = rng.choice(data)
        console.print(f"[bold]Array:[/bold] {data}")
        console.print(f"[bold]Target:[/bold] {target}")
        if algorithm == "linear_search":
            if visual:
                _safe_call("animate_binary_search", data, target, is_binary=False, delay_seconds=speed)
            idx = linear_search(data, target) if target is not None else -1
        else:
            if visual:
                _safe_call("animate_binary_search", data, target, is_binary=True, delay_seconds=speed)
            idx = binary_search(data, target) if target is not None else -1
        if visual:
            if idx != -1:
                console.print(f"[bold green]Found {target} at index {idx}[/bold green]")
            else:
                console.print(f"[bold red]{target} not found[/bold red]")
        console.print(f"[bold green]Index:[/bold green] {idx}")

    elif algorithm in {"bfs", "dfs"}:
        graph = generate_random_graph(rng, num_nodes=max(size, 1), edge_factor=2)
        start = next(iter(graph))
        console.print(f"[bold]Graph nodes:[/bold] {list(graph.keys())}")
        console.print(f"[bold]Start:[/bold] {start}")
        if algorithm == "bfs":
            order = bfs(graph, start)
        else:
            order = dfs(graph, start)
        if visual:
            if not _safe_call("animate_graph_traversal", graph, order, delay_seconds=speed):
                console.print(f"[bold green]Order:[/bold green] {order}")
        else:
            console.print(f"[bold green]Order:[/bold green] {order}")

    elif algorithm == "dijkstra":
        graph_w = generate_random_graph(rng, num_nodes=max(size, 2), edge_factor=2, weighted=True)
        start = next(iter(graph_w))
        dist = dijkstra(graph_w, start)
        if visual:
            _safe_call("animate_graph_traversal", {k: [n for n, _w in v] for k, v in graph_w.items()}, list(dist.keys()))
        console.print(f"[bold green]Distances from {start}:[/bold green] {dist}")

    else:
        available = ", ".join(sum(ALGO_CATEGORIES.values(), []))
        raise click.UsageError(f"Unknown algorithm '{algorithm}'. Available: {available}")

    t1 = time.perf_counter()
    console.print(f"[dim]Elapsed: {(t1 - t0)*1000:.1f} ms[/dim]")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
