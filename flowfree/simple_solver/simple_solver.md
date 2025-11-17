# `simple_solver`

Cell-centric depth-first search with propagation. Each decision colours
an empty cell directly rather than extending colour “heads”.

## Approach

- **Search model:** DFS over empty cells using minimum-remaining-values (MRV) to
  pick the cell with the fewest candidate colours.
- **Per-colour reachability:** Before branching, BFS from each endpoint pair to
  determine which empties remain legal for that colour; dead branches are cut
  immediately.
- **Propagation rules:**
  - `force_single_color_cells` fills empties reachable by exactly one colour.
  - `force_degree_neighbors` enforces local degree caps (endpoint=1, connector=2)
    and fills neighbours when the remaining capacity matches the number of free
    cells.
- **Validity guards:** `Board.empty_regions_port_ok()` ensures every empty region
  touches at least two coloured ports to avoid dead pockets; `degree_ok_local`
  prevents over-saturating endpoints.
- **State management:** Lightweight board stores assignments and push/pop logs for
  quick backtracking.

## Solving Flow

1. Run reachability for every colour and apply the two propagation rules until no
   more forced moves exist.
2. Choose the next empty cell via MRV.
3. Branch over candidate colours, skipping any that violate local degree checks.
4. After each speculative paint, propagate again; if a contradiction arises,
   backtrack and try the next colour.
5. When the grid is full, verify local degree constraints to confirm a solution.

## Pros

- Solves all 90 benchmark puzzles within the 180 s limit.
- Extremely fast on most boards (≈4 ms median) because many puzzles finish during
  propagation alone.
- Straightforward code path makes new heuristics easy to integrate.

## Cons

- No transposition table, so identical dead states will be re-explored (but it's an easy fix if needed)
- Reachability is recomputed from scratch at each node; this dominates runtime on
  large, sparse boards.
- Runtime has a heavy tail on 10×10 “open” or “mixed” puzzles (longest run
  155 s).

## Benchmark Snapshot *(90 puzzles)*

- **Solve rate:** 100 % (90/90).
- **Median time:** 0.0041 s; **mean:** 5.19 s; **max:** 155.17 s.
- **Median search effort:** 7 attempts, 0 backtracks, 3 decision nodes, 62 nodes generated.
- **Propagation hits (median):** single-colour 0; single-degree 57.
- **Tag medians:** bottleneck 0.0034 s; many_colors 0.0021 s; tunnel 0.0039 s; open
  0.0083 s (mean 21.9 s due to long tail); mixed 0.0092 s.

### Detailed Benchmark Table (time cap 180 s)

| size | solved | timed_out | failed | success_rate | mean_time_s | mean_attempts | mean_backtracks | median_attempts | median_backtracks | mean_tree_depth | median_tree_depth | mean_single_color | mean_single_degree |
|------|-------:|----------:|-------:|-------------:|------------:|--------------:|----------------:|-----------------:|------------------:|----------------:|------------------:|------------------:|-------------------:|
| 5×5  | 15 | 0 | 0 | 100 % | 0.00078 | 2.73 | 0.47 | 0 | 0 | 1.00 | 0.0 | 0.40 | 19.47 |
| 6×6  | 15 | 0 | 0 | 100 % | 0.00263 | 12.40 | 2.47 | 4 | 0 | 2.33 | 1.0 | 0.00 | 48.07 |
| 7×7  | 15 | 0 | 0 | 100 % | 0.00404 | 8.20 | 1.07 | 5 | 0 | 2.20 | 1.0 | 0.07 | 49.47 |
| 8×8  | 15 | 0 | 0 | 100 % | 0.17382 | 987.67 | 195.60 | 7 | 0 | 5.40 | 3.0 | 0.07 | 1848.47 |
| 9×9  | 15 | 0 | 0 | 100 % | 0.28077 | 586.93 | 95.13 | 21 | 1 | 6.33 | 8.0 | 0.20 | 4587.47 |
| 10×10| 15 | 0 | 0 | 100 % | 30.67340 | 68 958.93 | 9675.07 | 182 | 29 | 10.13 | 9.0 | 184.07 | 150 114.27 |

**Overall:** 90/90 solved (100.0%).

## Notes

- Reachability sets per colour, although recomputed frequently, provide powerful
  pruning.
- Although average branching factors are higher than head-based solvers (since move candidates are based on coloring cells), the depth is lower, leading to manageable search trees.
- Propagation rules pretty much carry the process on many puzzles, minimizing search effort.