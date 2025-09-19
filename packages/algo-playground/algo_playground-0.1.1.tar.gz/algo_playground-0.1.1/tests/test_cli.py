from __future__ import annotations

import re
from click.testing import CliRunner

from algo_playground.cli import cli


def test_cli_list() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "Available Algorithms" in result.output
    assert "bubble_sort" in result.output
    assert "binary_search" in result.output
    assert "dijkstra" in result.output


def test_cli_run_quick_sort_no_visual() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["run", "quick_sort", "--size", "10"])
    assert result.exit_code == 0
    assert "Sorted:" in result.output
    assert "Elapsed:" in result.output


def test_cli_run_binary_search_visual_fast() -> None:
    runner = CliRunner()
    # Visual with speed 0 to avoid delays
    result = runner.invoke(
        cli, ["run", "binary_search", "--size", "10", "--visual", "--speed", "0"]
    )
    assert result.exit_code == 0
    assert "Array:" in result.output
    assert re.search(r"Index:\s+-?\\d+", result.output) or "Found" in result.output
