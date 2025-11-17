# `improved_port`

Head-extending search derived from the `python_port` solver, augmented with
stronger propagation, validators, and a transposition table.

## Approach

- **Search model:** Extends active colour “heads” cell by cell. Active states are
  prioritised by the number of unassigned neighbours; ties use BFS distance to
  the partner endpoint.
- **Propagation stack:**
  - `SingleNeighbor` forces a head that has only one legal move.
  - `SingleDomain` attaches an empty cell whose domain has collapsed to a single
    colour and touches an active head.
  - `CutVertexBridge` forces cells whose removal disconnects active endpoints.
  - Forward checking (`FC.Maintain_for`) ripples domain pruning after each move.
- **Validators:** `empty_domains_ok`, `dead_end_ok`, `empty_regions_ok`,
  `frontier_guard_ok`, `endpoints_reachable_ok` are applied after propagation to
  prune dead branches early.
- **Transposition table:** LRU cache (~3 M entries) keyed by board string; avoids
  re-exploration of disproven states.
- **Colour completion:** When a colour reaches both endpoints with correct
  degrees, the solver removes that colour from neighbouring domains and deactivates
  its heads.

## Solving Flow

1. Loop propagation rules until no change occurs.
2. Validate domains/reachability; abort the branch if any check fails.
3. Check the transposition table; skip states known to be dead.
4. Sort active heads, generate candidate moves, order them by MRV + BFS.
5. Assign a move, run forward checking, revalidate, then recurse.
6. On backtrack, undo propagation frames (including FC history) and reactivate
   heads/restore domains.

## Pros

- Propagation and forward checking slash search effort on structured puzzles
  (tunnel, many_colors).
- Transposition table provides meaningful reuse on symmetric boards.
- Branching factor is typically small (median 2 choices) thanks to head-centric
  moves and propagation.

## Cons

- 10 puzzles (mostly 8×8–10×10 open/symmetric boards) exhaust the 180 s cap.
- Propagation overhead is heavy; when heuristics stall, the solver spends most
  time in forced-move loops without progressing.
- Complexity is higher than `simple_solver`; debugging requires understanding the
  interplay between propagators, validators, and FC.

## Benchmark Snapshot *(90 puzzles)*

- **Solve rate:** 88.9 % (80/90).
- **Median time (solved cases):** 0.0098 s; **mean:** 3.11 s; **max:** 76.08 s.
- **Median search effort:** 2 attempts, 0 backtracks, 52 nodes generated.
- **Propagation hits (median):** SingleNeighbor 42.5; SingleDomain 0;
  CutVertexBridge 0; TT hits median 0 (mean 156).
- **Hard failures:** open 8×8 #2119/#2711; open/snakes/symmetric 9×9 #2447,
  #2607, #2874, #2881; open/bottleneck 10×10 #2990/#2992; symmetric 10×10 #2972.
- **Tag medians:** tunnel 0.012 s (12/12 solved); many_colors 0.0065 s; open
  0.004 s median (solved subset) but mean 12.7 s with 6/12 solves.

### Detailed Benchmark Table (time cap 180 s)

| size | solved | timed_out | failed | success_rate | mean_time_s | mean_attempts | mean_backtracks | median_attempts | median_backtracks | mean_tree_depth | median_tree_depth | mean_single_neighbor | mean_single_domain | mean_cutvertex_bridge | mean_tt_hits |
|------|-------:|----------:|-------:|-------------:|------------:|--------------:|----------------:|-----------------:|------------------:|----------------:|------------------:|---------------------:|-------------------:|----------------------:|-------------:|
| 5×5  | 15 | 0 | 0 | 100 % | 0.00528 | 6.60 | 5.80 | 0 | 0 | 0.80 | 0.0 | 29.67 | 10.40 | 2.07 | 0.13 |
| 6×6  | 15 | 0 | 0 | 100 % | 0.29053 | 407.40 | 405.60 | 1 | 0 | 2.53 | 1.0 | 1391.13 | 437.33 | 244.67 | 49.27 |
| 7×7  | 15 | 0 | 0 | 100 % | 5.85803 | 4373.40 | 4371.27 | 3 | 0 | 3.47 | 2.0 | 26 978.87 | 8616.93 | 4736.40 | 566.33 |
| 8×8  | 13 | 2 | 0 | 86.7 % | 0.53098 | 8666.87 | 8666.07 | 0 | 0 | 3.53 | 0.0 | 71 321.40 | 15 960.87 | 20 072.20 | 759.47 |
| 9×9  | 10 | 5 | 0 | 66.7 % | 9.60728 | 19 116.47 | 19 113.80 | 516 | 512 | 9.13 | 7.0 | 211 502.80 | 42 714.33 | 45 275.47 | 1556.67 |
| 10×10| 12 | 3 | 0 | 80.0 % | 4.45004 | 7153.20 | 7150.00 | 9 | 2 | 7.67 | 4.0 | 93 302.60 | 14 282.47 | 32 040.00 | 608.73 |

**Overall:** 80/90 solved (88.9%).

## Notes

- Forced moves alone solve most small puzzles without branching, explaining the
  zero median attempts/backtracks on 5×5–7×7 boards.
- Open and high-empty-ratio puzzles overwhelm head-ordering heuristics; further
  congestion-aware tie-breakers or hybrid strategies could reduce timeouts.
- Forward checking dramatically reduces domain sizes but adds overhead; profiling
  shows it is the main cost once propagation stalls.
