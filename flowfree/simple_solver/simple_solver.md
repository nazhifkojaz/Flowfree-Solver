# `simple_solver` (Reachability + forced moves + DFS)

A take on a simpler approach, using reachability cells set per color, combined with forced moves and DFS. It's not a head-extending search, but more like a global "try c color in this cell" search.

## How it works

- **Compute reachability**: for each color, BFS from one endpoint to the other endpoint, storing reachable empty cells for that color.
- **Forced moves/propagations**: just like `improved_port`, repeatedly apply forced moves until no more can be applied. Forced moves are:
    - `SingleColor`: if an empty cell can only be filled by one color, force the move (though quite rare).
    - `SingleDegree`: when a colored cell has exactly the same amount of empty neighbors as the amount required by its degree limit (1 for endpoints, 2 for connector cells), force the move to the empty neighbors.
- **DFS when no more forced moves**: pick the empty cells with the smallest domain (MRV, again!), and try each color, then recurse.
---

## Benchmark summary (time cap: 3 minutes per puzzle)

| size | solved | timed_out | failed | success_rate | mean_attempts | median_attempts | mean_backtracks | median_backtracks | mean_tree_depth | median_tree_depth | single_color_mean | single_color_median | single_degree_mean | single_degree_median |
|------|-------:|----------:|-------:|-------------:|--------------:|-----------------:|----------------:|------------------:|----------------:|------------------:|------------------:|--------------------:|-------------------:|----------------------:|
| 5x5  | 15 | 0 | 0 | 100% | 2.733 |	0.0 |	0.467 |	0.0 |	1.000 |	0.0 |	0.400 |	0.0 |	19.467 |	17.0 |
| 6x6  | 15 | 0 | 0 | 100% | 12.400 |	4.0 |	2.467 |	0.0 |	2.333 |	1.0 |	0.000 |	0.0 |	48.067 |	26.0 |
| 7x7  | 15 | 0 | 0 | 100% |  8.200 |	5.0 |	1.067 |	0.0 |	2.200 |	1.0 |	0.067 |	0.0 |	49.467 |	42.0 |
| 8x8  | 15 | 0 | 0 | 100% | 987.667 |	7.0 |	195.600 |	0.0 | 	5.400 |	3.0 |	0.067 |	0.0 |	1848.467 |	52.0 |
| 9x9  | 15 | 0 | 0 | 100% | 586.933 |	21.0 |	95.133 |	1.0 |	6.333 |	8.0 |	0.200 |	0.0 |	4587.467 |	197.0 |
| 10x10| 15 | 0 | 0 | 100% | 68958.933 |	182.0 |	9675.067 |	29.0 |	10.133 |	9.0 |	184.067 |	0.0 |	150114.267 |	641.0 |
  


**Overall:** 90/90 solved (100.0%).

---

## Notes
- Surprisingly good, all puzzles are solved within the 180s time cap, even the 10x10 puzzles, beating both `python_port` and over-engineered `improved_port`.
- I think the reachability cells set per color is very effective though a bit costly to compute.
- The forced moves/propagations are also very effective (as seen in `improved_port`), especially the `SingleDegree`.
- Though it's not shown in the benchmark summary, the number of average/max branching is higher than `improved_port`, since it's "trying c colors in this cell" instead of "extending head to neighbor cells", so the search tree is wider (but shallower).
- Still quite struggling with some open puzzles, though not as bad as `improved_port`.
