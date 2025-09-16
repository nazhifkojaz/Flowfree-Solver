from collections import deque
from .state import State, Record


class FC:
    History: list[list[Record]] = []

    @staticmethod
    def Reset() -> None:
        FC.History.clear()

    @staticmethod
    def Maintain_for(changed: list[State]) -> None:

        frame: list[Record] = []
        q: deque[State] = deque()
        in_q: set[State] = set()

        #
        for state in changed:
            # remove this guard later once it's no longer needed
            if state is None:
                continue

            # put changed states to q
            if state not in in_q:
                q.append(state)
                in_q.add(state)

            # put their unassigned neighbors
            for neighbor in state.GetUnassignedPeers():
                if neighbor not in in_q:
                    q.append(neighbor)
                    in_q.add(neighbor)

            # if they are assigned, put the same-valued neighbors
            if state._value != -1:
                c = state._value
                for nb in state._peers:
                    if nb._value == c and nb not in in_q:
                        q.append(nb)
                        in_q.add(nb)

        while q:
            cell = q.popleft()

            # prune domains
            recs = cell.MaintainDomains()

            # skip if empty
            if not recs:
                continue

            frame.extend(recs)

            # ripples till no changes
            for rec in recs:
                for affected in rec.AffectedPeers:
                    if affected._value == -1 and affected not in in_q:
                        q.append(affected)
                        in_q.add(affected)
                    for neighbor in affected.GetUnassignedPeers():
                        if neighbor not in in_q:
                            q.append(neighbor)
                            in_q.add(neighbor)

        FC.History.append(frame)

    @staticmethod
    def Restore() -> None:
        if not FC.History:
            return
        frame = FC.History.pop()
        for rec in reversed(frame):
            val = rec.Value
            for peer in rec.AffectedPeers:
                if peer._value == -1 and val not in peer._domain:
                    peer._domain.append(val)
