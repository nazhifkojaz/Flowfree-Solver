from .fc import FC
from collections import deque


class SingleNeighbor:
    """
    Extend a head/frontier when they only have one legal neighbor.
    """

    @staticmethod
    def run(board, seeds, stats):
        moves = []
        stack = list(seeds)
        while stack:
            cur = stack.pop()
            if not cur._active:
                continue

            c = cur._value

            # current degree/connectivity for this color at the head
            deg_cur = sum(1 for p in cur._peers if p._value == c)

            # can't connect to any cell anymore
            if deg_cur > 1:
                continue

            # if it's an endpoint, then can't connect to more than one
            if cur._preassigned and deg_cur >= 1:
                continue

            # legal moves
            cands = [p for p in cur.GetUnassignedPeers() if c in p._domain]
            if len(cands) != 1:
                continue

            # quick sanity check
            peer = cands[0]
            if c not in peer._domain:
                continue

            # update the stats
            stats["single_neighbor"] = stats.get("single_neighbor", 0) + 1

            # assignments
            cur._active = False
            peer._value = c
            deg_peer = sum(1 for p in peer._peers if p._value == c)
            peer._active = deg_peer == 1

            FC.Maintain_for([peer, cur])

            moves.append((cur, peer))

            # if it's still an active state, see if we can still do a force move
            if peer._active:
                stack.append(peer)
        return moves

    @staticmethod
    def undo(chain):
        for cur, peer in reversed(chain):
            FC.Restore()
            peer._value = -1
            peer._active = False
            cur._active = True


class SingleDomain:
    """
    If an unassigned cell has a single legal value (single domain, c) and exactly one neighbor (head/frontier) with c-value,
    attach itself to that neighbor, and move the head to this cell instead.
    """

    @staticmethod
    def run(board, stats):
        moves = []
        changed = True
        while changed:
            changed = False
            for s in list(board.UnassignedStates()):
                if len(s._domain) != 1:
                    continue
                c = s._domain[0]

                # find a peer with same color
                adj_c = [n for n in s._peers if n._value == c]
                if len(adj_c) != 1:
                    continue
                n = adj_c[0]

                # T-guard
                if not n._active:
                    continue

                stats["single_domain"] = stats.get("single_domain", 0) + 1
                n._active = False
                s._value = c

                # active by degree
                s._active = sum(1 for p in s._peers if p._value == c) == 1
                FC.Maintain_for([s, n])

                moves.append((s, n))
                changed = True
        return moves

    @staticmethod
    def undo(singles):
        for s, prev_active in reversed(singles):
            FC.Restore()
            s._value = -1
            if s._active:
                s._active = False
            if prev_active is not None:
                prev_active._active = True


class CutVertexBridge:
    """
    Check any currently connected (through c-color and unassigned) endpoints,
    try snip one (s) of unassigned cells in between,
    if it disconnect them, force a move to that unassigned cell (s).
    """

    @staticmethod
    def _reachable_without(
        board, color: int, start_id: int, goal_id: int, blocked
    ) -> bool:
        q = deque([start_id])
        seen = {start_id}
        while q:
            u_id = q.popleft()
            if u_id == goal_id:
                return True
            u = board._states[u_id]
            for v in u._peers:
                # skip the blocked cell
                if v is blocked:
                    continue

                # only pass through unassigned (With color in domain) or c-colored cells
                if not ((v._value == -1 and color in v._domain) or (v._value == color)):
                    continue
                vid = v._id
                if vid in seen:
                    continue
                seen.add(vid)
                q.append(vid)
        return False

    @staticmethod
    def run(board, stats):
        fills = []
        changed = True
        while changed:
            changed = False

            # iterate set of colors that currently have any frontier/heads
            actives = board.GetActiveStates()
            colors = sorted({s._value for s in actives})
            if not colors:
                break

            for c in colors:
                start_id, goal_id = board.GetActiveHeads(c)
                if start_id is None or goal_id is None:
                    continue

                # quick reachability: if ends are not connected, skip color
                if not CutVertexBridge._reachable_without(
                    board, c, start_id, goal_id, blocked=None
                ):
                    continue

                # Try each empty cell that can carry c as the candidate bridge
                for s in board.UnassignedStates():
                    if c not in s._domain:
                        continue

                    # If removing s disconnects the ends, then s must be c
                    if not CutVertexBridge._reachable_without(
                        board, c, start_id, goal_id, blocked=s
                    ):
                        # assign
                        s._value = c

                        # new frontier if degree(c) at s is 1
                        deg = sum(1 for p in s._peers if p._value == c)
                        s._active = (deg <= 1) if s._preassigned else (deg == 0)

                        FC.Maintain_for([s])
                        # fills.append((s, refresh_frontiers))
                        stats["cutvertex_bridge"] = stats.get("cutvertex_bridge", 0) + 1
                        fills.append(s)

                        changed = True
                        break  # one change at a time
                if changed:
                    break
        return fills

    @staticmethod
    def undo(fills):
        for s in reversed(fills):
            FC.Restore()
            s._value = -1
            if s._active:
                s._active = False
