# `improved_port` (improved with forced moves & validators)

Based on `python_port`, added forced moves (propagations), better validators, and stronger domain maintenance to prune dead domain/branches earlier.

## How it works

More or less the same as `python_port` but with added pre-DFS propagations to push forced moves in early states.

## What’s new vs `python_port`

- **Stronger domain maintenance**: in `python_port`, MaintainDomains is only applied to assigned cells; here it's applied to unassigned cells, as well as checking its neighbors' domains for possible domain pruning.
- **Ripple-effect FC**: after each move, repeatedly apply domain maintenance until there are no more changes/affected cells.
- **Forced moves/propagations**: before branching, repeatedly apply propagatos/forced moves until no more can be applied. Forced moves are:
    - `SingleNeighbor`: if an active head has only one valid neighbor, force the move.
    - `SingleDomain`: if an empty cell can only be filled by one color and has a active neighbor of that color, force the move.
    - `CutVertexBridge`: when a cell is removed from the graph and it disconnects the endpoints, force the move to that cell.
- **Stronger validators**: added more validators to exit early on dead branches.
    - `empty_domains_ok()`: no cell has an empty domain.
    - `dead_end_ok()`: no dead end singletons.
    - `endpoints_reachable_ok()`: for every color, there’s a path through cells that are `c` or allow `c`.
    - `empty_regions_ok()`: no empty region is too small to fit the colors that must cross it (simple capacity check).
    - `frontier_guard_ok()`: unfinished colors must have at least one active head.
- **Completed color pruning**: once a color is completed, remove it from all unassigned cells' domains and mark all active heads of that color as inactive.
- **TT (transposition table)**: store previously explored dead branches/board states to avoid re-exploration.
---

## Benchmark summary (time cap: 3 minutes per puzzle)

| size | solved | timed_out | failed | success_rate | mean_attempts | median_attempts | mean_backtracks | median_backtracks | mean_tree_depth | median_tree_depth | single_neighbor_mean | single_neighbor_median | single_domain_mean | single_domain_median | cutvertex_bridge_mean | cutvertex_bridge_median | tt_hits_mean | tt_hits_median |
|------|-------:|----------:|-------:|-------------:|--------------:|-----------------:|----------------:|------------------:|----------------:|------------------:|----------------------:|-----------------------:|------------------:|---------------------:|----------------------:|------------------------:|-------------:|---------------:|
| 5x5  | 15 | 0 | 0 | 100.0% | 6.600 |	0.0 |	5.800 |	0.0 |	0.800 |	0.0 |	29.667 |	17.0 |	10.400 |	0.0 |	2.067 |	0.0 |	0.133 |	0.0 |
| 6x6  | 15 | 0 | 0 | 100.0% | 407.400 |	1.0 |	405.600 |	0.0 |	2.533 |	1.0 |	1391.133 |	28.0 |	437.333 |	0.0 |	244.667 |	0.0 |	49.267 |	0.0 |
| 7x7  | 15 | 0 | 0 | 100.0% | 4373.400 |	3.0 |	4371.267 |	0.0 |	3.467 |	2.0 |	26978.867 |	38.0 |	8616.933 |	0.0 |	4736.400 |	0.0 |	566.333 |	0.0 |
| 8x8  | 13 | 2 | 0 | 86.7% | 9386.533 |	0.0 |	9385.733 |	0.0 |	3.533 |	0.0 |	76962.200 |	50.0 |	17294.467 |	0.0 |	21873.267 |	11.0 |	821.467 |	0.0 |
| 9x9  | 10 | 5 | 0 | 66.7% | 18768.533 |	516.0 |	18765.867 |	512.0 |	9.133 |	7.0 |	207265.667 |	2932.0 |	41725.800 |	1168.0 |	44109.533 |	572.0 |	1532.267 |	38.0 |
| 10x10| 12 | 3 | 0 | 80.0% | 6698.867 |	9.0 |	6695.667 |	2.0 |	7.667 |	4.0 |	86733.467 |	90.0 |	13328.667 |	7.0 |	29998.067 |	22.0 |	563.467 |	0.0 |


**Overall:** 80/90 solved (88.9%).

---

## Notes

- Significant improvement over the basic `python_port`, most smaller puzzles are solved by forced moves alone, without entering DFS (explains the very low/zero attempts/backtracks/tree_depth for smaller puzzles).
- While the propagations really shines in smaller puzzles or corridor-like puzzle, it still struggles with snake-y or open puzzles, probably due to the heuristics (for snake-y puzzles, the heads are far apart so bad heuristics can lead to exploring wrong branches first), and for open puzzles, inability to effectively prune domains is still an issue.
