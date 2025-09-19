## algo-playground

Interactive terminal playground for classic algorithms (sorting, searching, graphs).

- Beginner-friendly, step-by-step visualizations in your terminal using Rich
- CLI to list and run algorithms with adjustable speed and data size
- Pure, type-hinted Python library you can import and reuse

### Installation
```bash
pip install algo-playground
```

Python 3.9+ is required.

### Quick Start
- List algorithms:
```bash
algo-playground list
```

- Run quick sort on 20 elements with visualization:
```bash
algo-playground run quick_sort --size 20 --visual --speed 0.05
```

- Binary search over a generated sorted list:
```bash
algo-playground run binary_search --size 30 --target 15
```

- BFS traversal on a generated graph (shows a quick graph drawing, then a live adjacency view):
```bash
algo-playground run bfs --size 8 --visual --speed 0.08
```

### CLI Reference
The CLI provides two commands: `list` and `run`.

- List available algorithms
```bash
algo-playground list
```

- Run an algorithm
```bash
algo-playground run <algorithm> [--size N] [--visual] [--speed S] [--target T] [--seed SEED]
```

- Common options
- **--size**: dataset size (array length or number of nodes). Default 20
- **--visual**: enable step-by-step, colored animations in the terminal
- **--speed**: delay between visual steps in seconds (e.g. 0.02, 0.1). Default 0.02
- **--seed**: seed for reproducible random data
- Searching only: **--target**: the value to find (picked randomly if omitted)

- Supported algorithms
- Sorting: `bubble_sort`, `merge_sort`, `quick_sort`
- Searching: `linear_search`, `binary_search`
- Graph: `bfs`, `dfs`, `dijkstra`

Examples
```bash
# Sorting
algo-playground run bubble_sort --size 15 --visual --speed 0.04
algo-playground run merge_sort --size 25
algo-playground run quick_sort --size 20 --visual

# Searching
algo-playground run linear_search --size 20 --target 7 --visual --speed 0.03
algo-playground run binary_search --size 30 --target 15 --visual

# Graphs
algo-playground run bfs --size 10 --visual --speed 0.08
algo-playground run dfs --size 10 --visual
algo-playground run dijkstra --size 10 --visual
```

### Visualizations
- Sorting
- Colored bars represent values
- Yellow = compare, Red = swap, Blue = normal
- Indices are shown above bars, with step/phase status

- Searching
- Array is shown as bars
- For binary search, pointers `lo`, `mid`, `hi` are labeled under the array
- Step status shows progress and results

- Graphs
- A quick ASCII drawing places nodes around a circle with arrows indicating edge directions
- Then an interactive live view displays the adjacency list, highlighting the current and visited nodes

Tip: Increase `--speed` for slower, more guided visuals.

### Python Library Usage
You can import and reuse the algorithms as pure functions.

Sorting
```python
from algo_playground.algorithms.sorting import bubble_sort, merge_sort, quick_sort

arr = [5, 3, 8, 2]
sorted_arr, comparisons = quick_sort(arr)
print(sorted_arr)  # [2, 3, 5, 8]
print(comparisons) # comparisons performed
```

Searching
```python
from algo_playground.algorithms.searching import linear_search, binary_search

arr = [1, 3, 5, 7, 9]
print(linear_search(arr, 7))  # 3
print(binary_search(arr, 5))  # 2
```

Graphs
```python
from algo_playground.algorithms.graphs import bfs, dfs, dijkstra

graph = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["D"],
    "D": [],
}
print(bfs(graph, "A"))  # ['A', 'B', 'C', 'D']
print(dfs(graph, "A"))  # ['A', 'B', 'D', 'C']

weighted = {
    "A": [("B", 2), ("C", 5)],
    "B": [("C", 1), ("D", 4)],
    "C": [("D", 1)],
    "D": [],
}
print(dijkstra(weighted, "A"))  # {'A':0, 'B':2, 'C':3, 'D':4}
```

### Tracing Hooks (Advanced)
Sorting algorithms can emit fine-grained steps for visualization. You can attach a callback:
```python
from algo_playground.algorithms.sorting import quick_sort, SortStep

arr = [4, 2, 6]

def on_step(step: SortStep) -> None:
    # inspect step.array, step.compare_indices, step.swap_indices
    pass

sorted_arr, comparisons = quick_sort(arr, trace=True, on_step=on_step)
```

### FAQ
- The `algo-playground` command isn’t found
  - Ensure your virtualenv is active, or add `~/.local/bin` to your PATH if using `--user`
- Visuals flicker or look odd in some terminals
  - Try a TrueColor-capable terminal and a monospaced font
- Graph drawing looks crowded
  - Reduce `--size` or increase terminal width; the live adjacency view remains clear

### License
MIT
