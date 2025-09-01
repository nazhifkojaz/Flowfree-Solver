from csp_state import State, Record


class FC:
    History: list[list[Record]] = []

    @staticmethod
    def Reset() -> None:
        FC.History.clear()

    # @staticmethod
    # def Maintain(board: "Board") -> None:
    #     frame: list[Record] = []
    #     for st in board.AssignedStates():
    #         rec = st.MaintainDomains()
    #         if rec is not None and rec.AffectedPeers:
    #             frame.append(rec)
    #     FC.History.append(frame)

    @staticmethod
    def Maintain_for(states: list[State]) -> None:
        frame: list[Record] = []
        for st in states:
            rec = st.MaintainDomains()
            if rec is not None and rec.AffectedPeers:
                frame.append(rec)
        FC.History.append(frame)

    @staticmethod
    def Restore() -> None:
        if not FC.History:
            return
        frame = FC.History.pop()
        if frame is not None:
            for rec in reversed(frame):
                val = rec.Value
                for peer in rec.AffectedPeers:
                    if peer._value == -1 and val not in peer._domain:
                        peer._domain.append(val)
