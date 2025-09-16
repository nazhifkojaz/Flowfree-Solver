from .csp_board import Board
from .csp_fc import FC

import time


class BtAlgo:
    def __init__(self, board: Board, TIME_CAP: float = 120.0):
        self._problem = board
        self._stats = {
            "attempts": 0,
            "backtracks": 0,
            "total_branching": 0,
            "max_branching": 0,
            "decision_node": 0,
            "tree_depth": 0,
            "time_s": 0,
        }

        self._time_cap = TIME_CAP
        self._t_start = time.perf_counter()

    def _elapsed(self) -> float:
        return time.perf_counter() - self._t_start

    def _other_active_for(self, color: int, exclude_id: int) -> int | None:
        for s in self._problem._states:
            if s._value == color and s._active and s._id != exclude_id:
                return s._id
        return None

    def search(self, depth: int = 0) -> bool:
        if depth > self._stats["tree_depth"]:
            self._stats["tree_depth"] = depth
        # finished scenario
        if self._problem.IsAssigned():
            self._stats["time_s"] = self._elapsed()
            return True

        actives = self._problem.GetActiveStatesOrdered()
        if not actives:
            return False

        # iterate through active states
        for current in actives:
            # stop when time_cap passed
            if self._elapsed() > self._time_cap:
                break

            current._active = False

            # iterate through current's unassigned peers
            # order by manhattan-distance to the color pair
            goal_id = self._other_active_for(current._value, current._id)
            if goal_id is None:
                # fallback only if somehow there isn't another active head
                goal_id = self._problem.GetColorPair(current._id, current._value)

            candidates = [
                p for p in current.GetUnassignedPeers() if current._value in p._domain
            ]
            candidates.sort(
                key=lambda p: (
                    len(p._domain),  # mrv
                    p.GetDistance(
                        goal_id, self._problem._width
                    ),  # manhattan distance as tiebreaker
                )
            )

            if candidates:
                self._stats["decision_node"] += 1
                self._stats["total_branching"] += len(candidates)
                if len(candidates) > self._stats["max_branching"]:
                    self._stats["max_branching"] = len(candidates)

            for peer in candidates:
                peer._active = True
                peer._value = current._value
                self._stats["attempts"] += 1

                # maintain domain for both current and selected peer
                FC.Maintain_for([current, peer])

                if self._problem.IsValid():
                    if self.search(depth + 1):
                        return True

                # Undo
                FC.Restore()
                self._stats["backtracks"] += 1
                peer._value = -1
                peer._active = False

            # reactivate the current again
            current._active = True

        # the branch has no solution
        self._stats["time_s"] = self._elapsed()
        return False
