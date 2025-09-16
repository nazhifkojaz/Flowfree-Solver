# `python_port` (python port for the C# implementation)

Python port of the original C# implementation, a simple head-extending FC + DFS solver. FC is used to prune/maintain domains and bookkeep for backtracking, and DFS explores the search space/tree based on MRV + distance ordering.

## How it works

- **State & Board**: Cells hold a single color value or `-1` for empty/unassigned cells.
- **Head‑extending search** (`csp_solver.py`): pick an *active* head bas
- **Forward Checking** (`csp_fc.py`): on each tentative move, filter neighbor domains; abort early if a domain becomes empty.
- **Backtracking**: if a move fails later, undo the FC log and try the next neighbor.
- **Variable ordering**: MRV (minimum remaining values) + manhattan distance tiebreaker (prefer candidates closer to target).
---

## Benchmark summary (time cap: 3 minutes per puzzle)

| size | solved | timed_out | failed | success_rate | mean_attempts | median_attempts | mean_backtracks | median_backtracks | mean_tree_depth | median_tree_depth |
|------|-------:|----------:|-------:|-------------:|--------------:|-----------------:|----------------:|------------------:|----------------:|------------------:|
| 5x5  | 12 | 3 | 0 | 80.0% | 3242346.467 |	27.0 |	3242333.533 |	12.0 |	16.067 |	17.0	|
| 6x6  | 11 | 4 | 0 | 73.3% | 3779006.267 |	39.0 |	3778987.600 |	11.0 |	25.000 |	26.0	|
| 7x7  | 8  | 7 | 0 | 53.3% | 5097769.667 |	60.0 | 	5097750.467 |	27.0 | 35.067 |	35.0	|
| 8x8  | 8  | 7 | 0 | 53.3% | 4373320.200 |	86.0 |	4373294.333 |	39.0 | 47.133 |	47.0 |
| 9x9  | 7  | 8 | 0 | 46.7% | 3967365.533 |	5297172.0 |	3967335.333 |	5297172.0	| 59.867 |	61.0 |
| 10x10| 3  | 12| 0 | 20.0% | 4374000.867 |	5465999.0 |	4373984.600 |	5465999.0 |	73.867 |	74.0 |

**Overall:** 49/90 solved (54.4%).

---

## Notes

- This solver is pretty basic and straightforward, with little to no optimization, the results are not very impressive.
- The number of attempts and backtracks are generally increasing with puzzle size due to the growth of search space.
- Showed both mean and median to illustrate the skewness of the data (the unsolved/timed_out puzzles can significantly skew the mean so the median is often more representative).
- For more detailed benchmark results, see `data/port_benchmark_result_3mins.csv`.