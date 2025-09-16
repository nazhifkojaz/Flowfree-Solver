from .board import Board
from .state import Record
from .fc import FC
from .state import State
from .validators import Validators
from .propagation import SingleNeighbor, SingleDomain, CutVertexBridge
from collections import OrderedDict

import time


class Solver:
    def __init__(
        self, board: Board, NODE_CAP: int = 3_000_000, TIME_CAP: float = 300.0
    ):
        self._problem = board
        self._node_cap = NODE_CAP
        self._time_cap = TIME_CAP
        self._stats = {
            "time_s": 0.0,
            "attempts": 0,
            "backtracks": 0,
            "total_branching": 0,
            "max_branching": 0,
            "tree_depth": 0,
            "decision_node": 0,
            "single_neighbor": 0,
            "single_domain": 0,
            "cutvertex_bridge": 0,
            "tt_hits": 0,
        }
        self._checks = Validators(board)
        self._tt = OrderedDict()
        self._tt_capacity = 3_000_000
        self._t_start = time.perf_counter()

    def _tt_key(self) -> str:
        return self._problem.AsString()

    def _tt_get(self, key):
        v = self._tt.get(key)
        if v is not None:
            self._tt.move_to_end(key)
        return v

    def _tt_set(self, key, value):
        self._tt[key] = value
        self._tt.move_to_end(key)
        if len(self._tt) > self._tt_capacity:
            print("not enough TT")
            self._tt.popitem(last=False)

    def _elapsed(self) -> float:
        return time.perf_counter() - self._t_start

    def _prune_completed_colors(self):
        recs: list[Record] = []
        deactivated: dict[int, list[State]] = {}
        colors = self._problem._colors
        for c in range(1, colors + 1):
            if self._checks.is_color_completed(c):
                # deactivate active heads for c color
                actives = [
                    s for s in self._problem._states if s._value == c and s._active
                ]
                if actives:
                    deactivated[c] = actives[:]
                    for s in actives:
                        s._active = False

                # remove c color from unassigned states
                affected = []
                for s in self._problem.UnassignedStates():
                    if c in s._domain:
                        s._domain.remove(c)
                        affected.append(s)
                if affected:
                    recs.append(Record(c, affected))
        return recs, deactivated

    def _other_active_for(self, color: int, exclude_id: int) -> int | None:
        for s in self._problem._states:
            if s._value == color and s._active and s._id != exclude_id:
                return s._id
        return None

    def _apply_force_moves(self):
        frames = []
        changed = True
        while changed:
            changed = False
            sn = SingleNeighbor.run(
                self._problem, self._problem.GetActiveStates(), self._stats
            )
            if sn:
                frames.append(("sn", sn))
                changed = True
                continue

            sd = SingleDomain.run(self._problem, self._stats)
            if sd:
                frames.append(("sd", sd))
                changed = True
                continue

            cvb = CutVertexBridge.run(self._problem, self._stats)
            if cvb:
                frames.append(("cvb", cvb))
                changed = True
                continue
        return frames

    def _undo_frames(self, frames):
        for tag, payload in reversed(frames):
            if tag == "cvb":
                CutVertexBridge.undo(payload)
            elif tag == "sd":
                SingleDomain.undo(payload)
            elif tag == "sn":
                SingleNeighbor.undo(payload)

    def search(self, depth: int = 0) -> bool:
        if depth > self._stats["tree_depth"]:
            self._stats["tree_depth"] = depth
        # pre-branching propagation
        preprop = self._apply_force_moves()
        ttkey = self._tt_key()
        if (
            not self._checks.empty_domains_ok()
            or not self._checks.endpoints_reachable_ok()
            or not self._checks.empty_regions_ok()
        ):
            self._tt_set(ttkey, False)
            self._undo_frames(preprop)
            return False

        # complete check
        if self._checks.fast_valid() and self._problem.IsAssigned():
            self._stats["time_s"] = self._elapsed()
            return True

        # TT update/check
        hit = self._tt_get(ttkey)
        if hit is False:
            self._stats["tt_hits"] += 1
            self._undo_frames(preprop)
            return False

        actives = self._problem.GetActiveStates()
        if not actives:
            self._tt_set(ttkey, False)
            self._undo_frames(preprop)
            return False

        actives.sort(key=lambda p: (len(p.GetUnassignedPeers())))

        for current in actives:
            if (self._stats["attempts"] > self._node_cap) or (
                self._elapsed() > self._time_cap
            ):
                self._stats["time_s"] = self._elapsed()
                break

            goal_id = self._other_active_for(current._value, current._id)
            if goal_id is None:
                # fallback only if somehow there isn't another active head
                goal_id = self._problem.GetColorPair(current._id, current._value)

            # get legal candidates
            candidates = [
                p for p in current.GetUnassignedPeers() if current._value in p._domain
            ]
            dist_map = self._problem.BfsDistancesToGoal(
                current._value, goal_id, candidates
            )
            unreachable = self._problem._width**2

            # If this head can't move now, try other heads
            if not candidates or all(
                dist_map.get(c._id, unreachable) >= unreachable for c in candidates
            ):
                # self._tt_set(ttkey, False)
                continue

            candidates.sort(
                key=lambda p: (
                    len(p._domain),  # MRV
                    dist_map.get(p._id, unreachable),  # bfs distance as tie breaker
                    # p.GetDistance(goal_id, self._problem._width)
                )
            )

            if candidates:
                self._stats["decision_node"] += 1
                self._stats["total_branching"] += len(candidates)
                if len(candidates) > self._stats["max_branching"]:
                    self._stats["max_branching"] = len(candidates)

            for peer in candidates:

                current._active = False
                peer._value = current._value
                deg_peer = sum(1 for q in peer._peers if q._value == peer._value)
                peer._active = deg_peer == 1

                self._stats["attempts"] += 1
                FC.Maintain_for([current, peer])

                if not (
                    self._checks.empty_domains_ok()
                    and self._checks.endpoints_reachable_ok()
                    and self._checks.empty_regions_ok()
                ):
                    FC.Restore()
                    self._tt_set(self._tt_key(), False)
                    peer._value = -1
                    if peer._active:
                        peer._active = False
                    current._active = True
                    self._stats["backtracks"] += 1
                    continue

                # if the color is completed, prune and deactivate heads
                pruned, deactivated = self._prune_completed_colors()
                if self._checks.fast_valid() and self.search(depth + 1):
                    return True

                for rec in reversed(pruned):
                    for st in rec.AffectedPeers:
                        if rec.Value not in st._domain:
                            st._domain.append(rec.Value)

                FC.Restore()
                peer._value = -1
                if peer._active:
                    peer._active = False
                current._active = True
                self._stats["backtracks"] += 1

                for c, nodes in deactivated.items():
                    if not self._checks.is_color_completed(c):
                        for st in nodes:
                            if st._value == c:
                                st._active = True

        self._tt_set(ttkey, False)
        self._undo_frames(preprop)
        return False
