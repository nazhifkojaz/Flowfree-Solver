# `pns_solver`

Proof-number search (PNS) implementation that treats FlowFree as a proof/disproof
game. Nodes maintain proof (`pn`) and disproof (`dn`) numbers that guide expansion
towards the most promising frontier.

## Approach

- **Search model:** Proof-number search on head moves. Each node
  represents a board state with active colour heads; expansion selects the child
  with minimal `(pn, dn)` (the “most proving node”). A node is “proved” when
  a completion is found and “disproved” when every child violates a constraint,
  so OR/AND aggregation rules still apply.
- **Propagation loop:** Before branching, the solver applies:
  - Colour reachability checks per endpoint pair.
  - Empty-region viability (`empty_regions_port_ok`).
  - Forced head moves when only one legal extension exists.
  - Degree-based forcing (`_force_degree_neighbors`) for endpoints/connectors.
- **Terminal detection:** Classifies states as solved/disproved before expansion
  when the board is complete, a colour disconnects, an empty strand is isolated,
  or no legal moves exist.
- **Transposition table:** Caches pn/dn values for explored boards keyed by the
  flattened grid, enabling large proof trees to reuse sub-results.
- **Move ordering:** Legal head moves ordered by number of empty neighbours and
  Manhattan distance to the partner endpoint to prioritise constrained moves.

## Solving Flow

1. Initialise root node with `pn=dn=1`.
2. Repeatedly select the most proving leaf (smallest `(pn, dn)` pair).
3. Expand: generate legal moves, clone the board, run propagation, classify
   terminal children, and cache them in the transposition table.
4. Update ancestor `pn/dn` values by aggregating child statistics (pn = min
   child pn; dn = sum of child dn with saturation guard).
5. Terminate when the root is proved (`pn==0`), disproved (`dn==0`), or the time
   / node cap is reached.

## Pros

- Proof-guided expansion keeps the average branching factor tiny (≈70 decision
  nodes per solved puzzle).
- Heavy transposition table reuse: mean 1.5k TT hits per puzzle (median 2).
- Propagation blend handles structured puzzles very efficiently (microsecond
  medians for bottleneck/many_colors/tunnel tags).

## Cons

- Six puzzles hit the 3-minute cap: open 9×9 #2607, snakes 9×9 #2874, bottleneck
  10×10 #2992, few_colors 10×10 #3041, open 10×10 #2963, symmetric 10×10 #2972.
- When proofs require broad exploration (open layouts), node counts explode,
  leading to long runs (max 163 s).
- Correct pn/dn bookkeeping and TT interactions make debugging a bit annoying.

## Benchmark Snapshot *(90 puzzles)*

- **Solve rate:** 93.3 % (84/90).
- **Median time:** 4.7e-07 s; **mean:** 3.05 s; **max:** 163.05 s (solved cases).
- **Median search effort:** 22 attempts, 0 backtracks, 23 nodes generated;
  expansions median 1.
- **Propagation hits (median):** calls 27.5, rounds 27, forced moves 45.5,
  degree moves 74.5, contradictions 4.
- **Tag medians:** bottleneck/many_colors/tunnel ≈0 s; open puzzles median 0.044 s
  with mean 16.97 s (two timeouts); mixed puzzles median 0.156 s.
- **Timeout summary:** 6 puzzles (listed above) exhausted the 180 s cap.

