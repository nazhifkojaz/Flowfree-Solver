from board import Board
from collections import deque


class Validators:
    def __init__(self, board: Board):
        self.board = board

    # this make sure that there are no unassigned cells with empty domains
    def empty_domains_ok(self) -> bool:
        for s in self.board._states:
            if s._value == -1 and not s._domain:
                return False
            if not s.IsConstraintsValid():
                return False
        return True

    # unfinished color need to have at least one active state
    def frontier_guard_ok(self) -> bool:
        for c in range(1, self.board._colors + 1):
            # quick active count first
            actives = 0
            any_c_cell = False
            for s in self.board._states:
                if s._value == c:
                    any_c_cell = True
                    if s._active:
                        actives += 1
            if actives >= 1:
                continue

            # no actives, check if the c color is completed
            if any_c_cell and self.is_color_completed(c):
                continue
            return False
        return True

    # all empty states must be reachable from active head
    def empty_regions_ok(self) -> bool:
        empties = self.board.UnassignedStates()
        seen = set()

        # collect active frontiers per color
        active_by_color = {}
        for s in self.board.GetActiveStates():
            active_by_color.setdefault(s._value, []).append(s)

        for s in empties:
            if s._id in seen:
                continue
            comp = {s._id}
            seen.add(s._id)
            q = [s]
            union_colors = set(s._domain)
            while q:
                u = q.pop()
                for v in u._peers:
                    if v._value == -1 and v._id not in seen:
                        seen.add(v._id)
                        comp.add(v._id)
                        q.append(v)
                        union_colors.update(v._domain)
            if not union_colors:
                return False

            # check if any active head/frontier can reach this component
            reachable = False
            for c in union_colors:
                for a in active_by_color.get(c, []):
                    if any(nb._value == -1 and nb._id in comp for nb in a._peers):
                        reachable = True
                        break
                if reachable:
                    break
            if not reachable:
                return False
        return True

    def endpoints_reachable_ok(self) -> bool:
        states = self.board._states
        for c in range(1, self.board._colors + 1):
            eps = [s for s in states if s._value == c and s._preassigned]
            if len(eps) != 2:
                continue  # incorrectly structured puzzle
            src, dst = eps
            q = deque([src._id])
            seen = {src._id}

            found = False
            while q:
                u_id = q.popleft()
                if u_id == dst._id:
                    found = True
                    break  # reachable
                u = states[u_id]
                for v in u._peers:
                    if v._id in seen:
                        continue
                    # pass through unassigned (with c in domain) or c-colored cells
                    if v._value == c or (v._value == -1 and c in v._domain):
                        seen.add(v._id)
                        q.append(v._id)
            if not found:
                # BFS exhausted, exit
                return False
        return True

    def fast_valid(self) -> bool:
        return (
            self.empty_domains_ok()
            and self.dead_end_ok()
            and self.empty_regions_ok()
            and self.endpoints_reachable_ok()
            and self.frontier_guard_ok()
        )

    def is_color_completed(self, color: int) -> bool:
        cells = [s for s in self.board._states if s._value == color]
        if not cells:
            return False
        eps = [s for s in cells if s._preassigned]
        if len(eps) != 2:
            return False
        start, goal = eps
        q = [start]
        seen = {start._id}
        reached = False
        while q:
            u = q.pop()
            if u._id == goal._id:
                reached = True
            for v in u._peers:
                if v._value == color and v._id not in seen:
                    seen.add(v._id)
                    q.append(v)
        if not reached:
            return False
        # degree check
        for s in cells:
            deg = sum(1 for p in s._peers if p._value == color)
            need = 1 if s._preassigned else 2
            if deg != need:
                return False
        return True

    def dead_end_ok(self) -> bool:
        for s in self.board._states:
            if s._value != -1:
                continue

            # If s has any empty neighbor, it's not a singleton → OK
            if any(nb._value == -1 for nb in s._peers):
                continue

            # Singleton: must touch a compatible, capacitated head
            ok = False
            for p in s._peers:
                if not p._active:
                    continue
                c = p._value
                if c not in s._domain:
                    continue
                # head capacity (endpoint cap=1, path cap=2)
                deg = sum(1 for q in p._peers if q._value == c)
                cap = 1 if p._preassigned else 2
                if deg < cap:
                    ok = True
                    break
            if not ok:
                return False
        return True
