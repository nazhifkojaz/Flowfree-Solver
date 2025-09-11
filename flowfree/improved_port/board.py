from collections import defaultdict, deque
from state import State
from fc import FC


class Board:
    def __init__(self, width: int, height: int, n_domain: int):
        self._width = width
        self._height = height
        self._colors = n_domain
        self._states: list[State] = []
        self._pairs: dict[int, list[int]] = defaultdict(list)  # color -> [endpoint ids]
        self.CreateStates(n_domain)
        self.ConnectStates()
        self.SanitizeDomains()

    def SanitizeDomains(self):
        FC.Reset()
        FC.Maintain_for(self.GetActiveStates())
        FC.Reset()

    def CreateStates(self, n_domain: int) -> None:
        self._states = [State(i, n_domain) for i in range(self._width * self._height)]

    def ConnectStates(self) -> None:
        W, H = self._width, self._height
        for r in range(H):
            for c in range(W):
                i = r * W + c
                s = self._states[i]
                if r > 0:
                    s._peers.append(self._states[(r - 1) * W + c])
                if r + 1 < H:
                    s._peers.append(self._states[(r + 1) * W + c])
                if c > 0:
                    s._peers.append(self._states[r * W + (c - 1)])
                if c + 1 < W:
                    s._peers.append(self._states[r * W + (c + 1)])

    def Preassign(self, mapping: dict[int, int]) -> None:
        self._pairs.clear()
        for cid, color in mapping.items():
            s = self._states[cid]
            s._value = color
            s._preassigned = True
            s._active = True  # endpoints start as active head
            if color not in s._domain:
                s._domain.append(color)
            self._pairs[color].append(cid)

    def GetActiveStates(self) -> list[State]:
        return [state for state in self._states if state._value != -1 and state._active]

    def UnassignedStates(self) -> list[State]:
        return [state for state in self._states if state._value == -1]

    def IsAssigned(self) -> bool:
        return all(state._value != -1 for state in self._states)

    def GetColorPair(self, current_id: int, color: int) -> int:
        ids = self._pairs.get(color, [])
        if len(ids) != 2:
            return current_id
        return ids[1] if ids[0] == current_id else ids[0]

    def GetActiveHeads(self, color: int):
        heads = [s for s in self.GetActiveStates() if s._value == color]
        if len(heads) >= 2:
            return heads[0]._id, heads[1]._id
        if len(heads) == 1:
            other = self.GetColorPair(heads[0]._id, color)
            return heads[0]._id, other
        return None, None

    def AsString(self) -> str:
        out = []
        for s in self._states:
            out.append("x" if s._value == -1 else str(s._value))
        return "".join(out)

    def BfsDistancesToGoal(
        self, color: int, goal_id: int, candidates: list[State]
    ) -> dict[int, int]:
        if not candidates:
            return {}

        unreachable = self._width * self._height + 1
        targets = {s._id for s in candidates}
        remaining = set(targets)
        dist: dict[int, int] = {}

        if goal_id in remaining:
            dist[goal_id] = 0
            remaining.remove(goal_id)

            # return early if goal is the only target
            if not remaining:
                return {t: dist.get(t, unreachable) for t in targets}

        q = deque([goal_id])
        seen = {goal_id}
        level = {goal_id: 0}

        while q and remaining:
            u = q.popleft()
            du = level[u] + 1
            u_state = self._states[u]

            for v in u_state._peers:
                if v._value != -1 and v._value != color:
                    continue
                if v._value == -1 and (color not in v._domain):
                    continue

                vid = v._id
                if vid in seen:
                    continue
                seen.add(vid)
                level[vid] = du
                q.append(vid)

                if vid in remaining:
                    dist[vid] = du
                    remaining.remove(vid)
                    if not remaining:
                        break

        for vid in targets:
            dist.setdefault(vid, unreachable)
        return dist
