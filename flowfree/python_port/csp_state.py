from dataclasses import dataclass


class State:
    def __init__(self, id_: int, domain: list[int]):
        self._id: int = id_
        self._value: int = -1
        self._domain: list[int] = list(domain)
        self._peers: list["State"] = []
        self._preassigned: bool = False
        self._active: bool = False

        # neighbor indices
        self.Top: int = -1
        self.Bot: int = -1
        self.Right: int = -1
        self.Left: int = -1

    def GetUnassignedPeers(self) -> list["State"]:
        unassigned: list[State] = []
        for peer in self._peers:
            if peer._value == -1:
                unassigned.append(peer)
        return unassigned

    def GetUnassignedPeersOrdered(self, id_: int, size: int) -> list["State"]:
        unassigned = self.GetUnassignedPeers()
        # Ordered by "distance" (the original C# implementation's GetDistance)
        unassigned.sort(key=lambda o: o.GetDistance(id_, size))
        return unassigned

    def MaintainDomains(self):
        if self._value == -1:
            return None

        affected: list["State"] = []

        if self._preassigned:
            # Endpoint: once exactly ONE same-color neighbor is attached,
            # remove this value from other peer's domain
            same = [peer for peer in self._peers if peer._value == self._value]
            if len(same) > 1:
                # Over-satisfied; invalid configuration; let IsConstraintsValid catch it.
                return None
            if len(same) == 1:
                anchor = same[0]._id
                for other in self._peers:
                    if other._id == anchor:
                        continue
                    if other._value == -1 and self._value in other._domain:
                        other._domain.remove(self._value)
                        affected.append(other)
                return Record(self._value, affected) if affected else None

        else:
            # Connectors: once TWO same-color neighbors are attached,
            # remove this value from other peer's domains.
            same_ids = [peer._id for peer in self._peers if peer._value == self._value]
            if len(same_ids) == 2:
                for other in self._peers:
                    if other._id in same_ids:
                        continue
                    if other._value == -1 and self._value in other._domain:
                        other._domain.remove(self._value)
                        affected.append(other)
                return Record(self._value, affected) if affected else None
            elif len(same_ids) > 2:
                return None

        return None

    def IsConstraintsValid(self) -> bool:
        if self._value == -1:
            return True

        assignedWithSameValue = 0
        unassigned = 0
        for peer in self._peers:
            if peer._value == self._value:
                assignedWithSameValue += 1
            elif peer._value == -1:
                unassigned += 1

        if self._preassigned:
            # Endpoint: degree <= 1 always
            if assignedWithSameValue > 1:
                return False
            if unassigned == 0 and assignedWithSameValue != 1:
                return False
        else:
            # Connectors
            if assignedWithSameValue > 2:
                return False
            if unassigned == 0 and assignedWithSameValue != 2:
                return False

        return True

    def GetDistance(self, target: int, boardSize: int) -> int:
        x1, y1 = self._id % boardSize, self._id // boardSize
        x2, y2 = target % boardSize, target // boardSize
        return abs(x1 - x2) + abs(y1 - y2)


@dataclass
class Record:
    Value: int
    AffectedPeers: list[State]
