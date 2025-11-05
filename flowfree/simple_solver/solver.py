import time

from .board import Board, EMPTY
from .propagation import Propagation, PropOutcome

from collections import deque
from flowfree.stats import ensure_keys, new_stats


class Solver:
    def __init__(self, board: Board, TIME_CAP: float = 300.0):
        self.b = board
        self.colors = list(self.b.colors)

        # number of cells (width * height)
        self.N = self.b.n

        self._final_board: list[int] | None = None

        self._stats = new_stats({"average_branching": 0.0})
        ensure_keys(
            self._stats,
            (
                "propagations_single_color",
                "propagations_single_degree",
            ),
        )

        self._time_cap = TIME_CAP
        self._time_start = time.perf_counter()

        # reachability dict (color -> set of empties reachable via {EMPTY or color})
        self.reach = {c: set() for c in self.colors}

    def _elapsed(self):
        return time.perf_counter() - self._time_start

    def get_stats(self) -> dict:
        if self._stats["decision_nodes"] > 0:
            self._stats["average_branching"] = round(
                self._stats["total_branching"] / self._stats["decision_nodes"], 2
            )
        else:
            self._stats["average_branching"] = 0.0
        # Treat each speculative attempt and forced propagation fill as a generated node.
        forced = (
            self._stats.get("propagations_single_color", 0)
            + self._stats.get("propagations_single_degree", 0)
        )
        self._stats["nodes_generated"] = self._stats["attempts"] + forced
        return dict(self._stats)

    def _compute_reachability(self):
        """
        For each color, perform a BFS from one endpoint to find all reachable empty cells
        and return False if the other endpoint is not reachable.
        """
        for c in self.colors:
            # only allow to walk on EMPTY or c color itself
            allowed = (EMPTY, c)
            seen = [False] * self.N
            start, goal = self.b.endpoints[c]
            q = deque([start])
            seen[start] = True
            reachable_empties = set()
            while q:
                u = q.popleft()
                for n in self.b.neighbors(u):
                    if not seen[n] and self.b.cells[n].value in allowed:
                        seen[n] = True
                        q.append(n)
                        if self.b.cells[n].value == EMPTY:
                            reachable_empties.add(n)

            if not seen[goal]:
                return False
            self.reach[c] = reachable_empties
        return True

    def _apply_force_moves(self) -> bool:
        while True:
            if not self._compute_reachability():
                return False
            if not self.b.empty_regions_port_ok():
                return False

            force_single = Propagation.force_single_color_cells(
                self.b, self.reach, self._stats
            )
            if force_single is PropOutcome.ERROR:
                return False
            changed = force_single is PropOutcome.CHANGED

            force_degree = Propagation.force_degree_neighbors(self.b, self._stats)
            if force_degree is PropOutcome.ERROR:
                return False

            changed = changed or (force_degree is PropOutcome.CHANGED)
            if not changed:
                return True

    def _select_mrv_cell(
        self, reach: dict[int, set[int]]
    ) -> tuple[int, list[int]] | None:
        """
        Pick an empty cell with the fewest candidate colors (MRV), return (idx, candidates).
        """
        best_cands: list[int] = []
        best_i = -1
        best_k = 1_000_000
        for i in range(self.N):
            if self.b.cells[i].value != EMPTY:
                continue
            cands = [c for c in self.colors if i in reach[c]]
            if len(cands) == 0:
                return None  # dead
            if len(cands) < best_k:
                best_k = len(cands)
                best_i = i
                best_cands = sorted(cands)

                # early exit on 1-candidate (should be caught by propagation though)
                if best_k == 1:
                    break
        return (best_i, best_cands)

    def _dfs(self, solution: list[str], depth: int = 0) -> bool:
        if depth > self._stats["tree_depth"]:
            self._stats["tree_depth"] = depth

        if self.b.is_full():
            if all(self.b.degree_ok_local(i) for i in range(self.N)):
                solution.append(self.b.to_string())
                self._final_board = [cell.value for cell in self.b.cells]
                return True
            return False

        # update reachability, exit on unreachable
        if not self._compute_reachability():
            return False

        # exit on dead candidate
        mrv = self._select_mrv_cell(self.reach)
        if mrv is None:
            return False
        best_i, best_cands = mrv

        # mark for backtrack
        mark = self.b.push()

        self._stats["decision_nodes"] += 1  # decision node
        self._stats["total_branching"] += len(best_cands)
        if len(best_cands) > self._stats["max_branching"]:
            self._stats["max_branching"] = len(best_cands)

        for col in best_cands:
            if self._elapsed() > self._time_cap:
                break

            # skip if coloring would violate local degree
            if not self.b.degree_ok_local(best_i, after_color=col):
                continue

            # paint a color
            self.b._set(best_i, col)
            self._stats["attempts"] += 1
            if self._apply_force_moves() and self._dfs(solution, depth + 1):
                self.b.pop(mark)
                return True
            self.b.pop(mark)
        self._stats["backtracks"] += 1
        return False

    def solve(self) -> str | None:
        solution: list[str] = []
        self._final_board = None
        if not self._apply_force_moves():
            self._stats["time_s"] = self._elapsed()
            return []
        self._dfs(solution)
        self._stats["time_s"] = self._elapsed()
        return solution[0] if solution else None

    def final_board_values(self) -> list[int] | None:
        if self._final_board is None:
            return None
        return list(self._final_board)
