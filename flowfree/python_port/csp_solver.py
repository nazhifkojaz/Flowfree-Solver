from csp_board import Board
from csp_fc import FC


class BtAlgo:
    def __init__(self, board: Board):
        self._problem = board
        self._stats = {
            "attempts": 0,
            "backtracks": 0,
            "total_branching": 0,
            "max_branching": 0,
            "decision_node": 0,
        }

    def search(self) -> bool:
        # finished scenario
        if self._problem.IsAssigned():
            return True
        else:
            actives = self._problem.GetActiveStatesOrdered()
            if not actives:
                return False

            # iterate through active states
            for current in self._problem.GetActiveStatesOrdered():
                current._active = False
                # iterate through current state's unassigned peers
                # order by distance to the color pair (goal)
                goal_id = self._problem.GetColorPair(current._id, current._value)

                candidates = current.GetUnassignedPeersOrdered(
                    goal_id, self._problem._width
                )
                candidates.sort(
                    key=lambda p: (
                        len(p._domain),
                        p.GetDistance(goal_id, self._problem._width),
                    )
                )

                if len(candidates) > 0:
                    self._stats["decision_node"] += 1
                    self._stats["total_branching"] += len(candidates)
                    self._stats["max_branching"] = max(
                        self._stats["max_branching"], len(candidates)
                    )

                for peer in candidates:
                    # assign peer with current color and make it active
                    if current._value not in peer._domain:
                        continue

                    peer._active = True
                    peer._value = current._value
                    self._stats["attempts"] += 1

                    # Forward-checking
                    FC.Maintain_for([peer])

                    if self._problem.IsValid():
                        if self.search():
                            return True

                    # Not a solution along this branch -> restore domains and backtrack
                    FC.Restore()

                    # Backtrack
                    self._stats["backtracks"] += 1
                    peer._value = -1
                    peer._active = False

            # failed
            current._active = True
            return False
