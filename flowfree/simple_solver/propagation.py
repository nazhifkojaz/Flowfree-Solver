from enum import IntEnum
from .board import Board, EMPTY


class PropOutcome(IntEnum):
    ERROR = -1
    NO_CHANGE = 0
    CHANGED = 1


class Propagation:
    @staticmethod
    def force_single_color_cells(
        b: Board, reach: dict[int, set[int]], stats: dict
    ) -> PropOutcome:
        """
        If an empty cell is reachable by exactly one color, assign it to that color.
        Fail if any empty has zero candidate colors.
        """
        changed = False
        N = b.n
        for i in range(N):
            if b.cells[i].value != EMPTY:
                continue
            candidates = [c for c, vis in reach.items() if i in vis]
            if len(candidates) == 0:
                return PropOutcome.ERROR
            if len(candidates) == 1:
                col = candidates[0]
                if not b.degree_ok_local(i, after_color=col):
                    return PropOutcome.ERROR
                b._set(i, col)
                stats["force_single_color"] += 1
                changed = True
        return PropOutcome.CHANGED if changed else PropOutcome.NO_CHANGE

    @staticmethod
    def force_degree_neighbors(b: Board, stats: dict) -> PropOutcome:
        """
        If a colored cell must reach a required degree (1 for endpoints, 2 otherwise)
        and the number of permissible empty neighbors equals the remaining requirement,
        fill them immediately. If local degree constraints are violated, fail.
        """
        changed = False
        N = b.n
        for i in range(N):
            val = b.cells[i].value
            if val == EMPTY:
                continue
            same = 0
            cand: list[int] = []
            for nb in b.adj[i]:
                v = b.cells[nb].value
                if v == val:
                    same += 1
                elif v == EMPTY and b.degree_ok_local(nb, after_color=val):
                    cand.append(nb)
            is_endpoint = i in b.endpoints[val]
            limit = 1 if is_endpoint else 2
            if same > limit:
                return PropOutcome.ERROR
            need = limit - same
            if need == 0:
                continue
            if len(cand) < need:
                return PropOutcome.ERROR
            if len(cand) == need:
                for nb in cand:
                    if not b.degree_ok_local(nb, after_color=val):
                        return PropOutcome.ERROR
                    b._set(nb, val)
                    stats["force_single_degree"] += 1
                    changed = True
        return PropOutcome.CHANGED if changed else PropOutcome.NO_CHANGE
