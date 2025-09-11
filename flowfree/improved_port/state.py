from dataclasses import dataclass


@dataclass
class Record:
    Value: int
    AffectedPeers: list["State"]


class State:
    def __init__(self, id: int, n_domain: int):
        self._id = id
        self._value: int = -1
        self._domain: list[int] = list(range(1, n_domain + 1))
        self._peers: list["State"] = []
        self._preassigned: bool = False
        self._active: bool = False

    def GetUnassignedPeers(self) -> list["State"]:
        return [p for p in self._peers if p._value == -1]

    def IsConstraintsValid(self) -> bool:
        if self._value == -1:
            return True
        same = sum(1 for p in self._peers if p._value == self._value)
        need = 1 if self._preassigned else 2
        return same <= need

    def _possible_neighbor_count(self, cell: "State", color: int) -> int:
        cnt = 0
        for p in cell._peers:
            if p._value == color:
                cnt += 1
            elif p._value == -1 and color in p._domain:
                cnt += 1
        return cnt

    def _possible_neighbor_with_snapshot(
        self, cell: "State", color: int, snap: dict
    ) -> int:
        # count the number of neighbor with c value, or unassigned neighbor with c in their domains
        cnt = 0
        for p in cell._peers:
            if p._value == color:
                cnt += 1
            elif p._value == -1:
                p_dom = snap.get(p, set(p._domain))
                if color in p_dom:
                    cnt += 1
        return cnt

    # Forward-checking: for each nearby unassigned cell, remove colors that cannot achieve degree 2 locally.
    def MaintainDomains(self) -> list[Record]:
        recs: list[Record] = []

        # if the cell/state assigned
        if self._value != -1:
            # prune around assigned cell based on its type (endpoints/connector)
            c = self._value
            same = [p for p in self._peers if p._value == c]
            cap = 1 if self._preassigned else 2

            # remove c color from others' domain if reach cap
            if len(same) >= cap:
                affected: list[State] = []
                same_ids = {p._id for p in same}
                for other in self._peers:
                    if other._id in same_ids:
                        continue
                    if other._value == -1 and c in other._domain:
                        other._domain.remove(c)
                        affected.append(other)
                if affected:
                    recs.append(Record(c, affected))
            return recs

        # for unassigned: enforce degree-2 feasibility for this cell and its unassigned neighbors
        to_check: list[State] = [self] + self.GetUnassignedPeers()

        # snapshot of the local domain
        dom_snap = {cell: set(cell._domain) for cell in to_check}
        to_remove: dict[State, list[int]] = {}

        for cell in to_check:
            for c in list(dom_snap[cell]):
                # if possible neigbor < 2, then remove c from its domain later
                if self._possible_neighbor_with_snapshot(cell, c, dom_snap) < 2:
                    to_remove.setdefault(cell, []).append(c)

        # bookkeeping the pruned and color
        pruned_by_color: dict[int, list[State]] = {}
        for cell, colors in to_remove.items():
            for c in colors:
                if c in cell._domain:
                    cell._domain.remove(c)
                    pruned_by_color.setdefault(c, []).append(cell)

        for c, cells in pruned_by_color.items():
            recs.append(Record(c, cells))
        return recs
