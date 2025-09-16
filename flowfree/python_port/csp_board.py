from .csp_state import State


class Board:
    def __init__(self, width: int, height: int, n_domain: int):
        # initialize the board
        self._nodesCount = 0
        self._colors = n_domain
        self._width = width
        self._height = height
        self.CreateStates(n_domain)
        self.ConnectStates()

    def CreateStates(self, n_domain: int) -> None:
        self._states: list[State] = []
        domain = list(range(1, n_domain + 1))
        for i in range(self._width * self._height):
            self._states.append(State(i, domain))

    def ConnectStates(self) -> None:
        for i in range(self._width * self._height):
            self._states[i]._peers.clear()
            col = i % self._width
            row = i // self._width

            if col - 1 >= 0:
                self._states[i]._peers.append(self._states[i - 1])
                self._states[i].Left = i - 1
            else:
                self._states[i].Left = -1

            if col + 1 < self._width:
                self._states[i]._peers.append(self._states[i + 1])
                self._states[i].Right = i + 1
            else:
                self._states[i].Right = -1

            if row - 1 >= 0:
                self._states[i]._peers.append(self._states[i - self._width])
                self._states[i].Top = i - self._width
            else:
                self._states[i].Top = -1

            if row + 1 < self._height:
                self._states[i]._peers.append(self._states[i + self._width])
                self._states[i].Bot = i + self._width
            else:
                self._states[i].Bot = -1

    def Preassign(self, preassignedStates: dict[int, int]) -> None:
        for idx, val in preassignedStates.items():
            self._states[idx]._value = val
            self._states[idx]._preassigned = True
            self._states[idx]._active = True

    def IsAssigned(self) -> bool:
        for state in self._states:
            if state._value == -1:
                return False
        return True

    def UnassignedStates(self) -> list[State]:
        temp: list[State] = []
        for state in self._states:
            if state._value == -1:
                temp.append(state)
        return temp

    def GetActiveStates(self) -> list[State]:
        temp: list[State] = []
        for state in self._states:
            if state._active:
                temp.append(state)
        return temp

    def GetActiveStatesOrdered(self) -> list[State]:
        temp = sorted(self.GetActiveStates(), key=lambda o: len(o.GetUnassignedPeers()))
        return temp

    def AssignedStates(self) -> list[State]:
        temp: list[State] = []
        for state in self._states:
            if state._value != -1:
                temp.append(state)
        return temp

    def IsValid(self) -> bool:
        for state in self._states:
            if not state.IsConstraintsValid():
                return False
        return True

    def GetColorPair(self, id_: int, color: int) -> int:
        endpoints = [
            state._id
            for state in self._states
            if state._preassigned and state._value == color
        ]
        if len(endpoints) == 2:
            return endpoints[0] if endpoints[1] == id_ else endpoints[1]
        return id_

    def AsString(self) -> str:
        out = []
        for state in self._states:
            if state._value == -1:
                out.append("x")
            else:
                out.append(str(state._value))
        return "".join(out)
