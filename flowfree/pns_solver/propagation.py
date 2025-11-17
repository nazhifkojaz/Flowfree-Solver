from collections import deque

from flowfree.stats import bump, ensure_keys

from .board import Board, Coord


class Propagation:
    @staticmethod
    def any_color_disconnected(board: Board) -> bool:
        for color, (a, b) in board.endpoints.items():
            if not board.bfs_reachable_same_or_empty(a, b, color):
                return True
        return False

    @staticmethod
    def stranded_empty_exists(board: Board) -> bool:
        """Conservative check: each empty must touch another empty or an extendable head."""
        for idx, value in enumerate(board.grid):
            if value != -1:
                continue
            valid = False
            for nb in board.neighbors(idx):
                if nb == -1:
                    continue
                if board.grid[nb] == -1 or board.extendable_head(nb):
                    valid = True
                    break
            if not valid:
                return True
        return False

    @staticmethod
    def _compute_color_reachability(
        board: Board,
    ) -> tuple[bool, dict[int, set[int]]]:
        total = board.width * board.height
        reach: dict[int, set[int]] = {}
        for color, (start, goal) in board.endpoints.items():
            allowed = (-1, color)
            seen = [False] * total
            dq = deque([start])
            seen[start] = True
            reachable_empties: set[int] = set()
            while dq:
                cur = dq.popleft()
                if cur == goal:
                    continue
                for nb in board.neighbors(cur):
                    if nb == -1 or seen[nb]:
                        continue
                    val = board.grid[nb]
                    if val in allowed:
                        seen[nb] = True
                        dq.append(nb)
                        if val == -1:
                            reachable_empties.add(nb)
            if not seen[goal]:
                return False, reach
            reach[color] = reachable_empties
        return True, reach

    @staticmethod
    def _force_degree_neighbors(
        board: Board, metrics: dict | None
    ) -> tuple[bool, bool]:
        changed = False
        total = board.width * board.height
        if metrics is not None:
            ensure_keys(metrics, ("propagations_degree_moves",))
        for idx in range(total):
            color = board.grid[idx]
            if color <= 0:
                continue
            same = 0
            candidates: list[int] = []
            for nb in board.neighbors(idx):
                val = board.grid[nb]
                if val == color:
                    same += 1
                elif val == -1 and board.degree_ok_local(nb, after_color=color):
                    candidates.append(nb)
            limit = 1 if board.is_endpoint(idx, color) else 2
            if same > limit:
                if metrics is not None:
                    bump(metrics, "propagations_contradictions")
                return False, False
            need = limit - same
            if need == 0:
                continue
            if len(candidates) < need:
                if metrics is not None:
                    bump(metrics, "propagations_contradictions")
                return False, False
            if len(candidates) == need:
                for nb in candidates:
                    if board.grid[nb] != -1:
                        continue
                    board.paint(nb, color)
                    changed = True
                    if metrics is not None:
                        bump(metrics, "propagations_degree_moves")
        return True, changed

    @staticmethod
    def run(board: Board, metrics: dict | None = None) -> bool:
        """
        Apply safe propagation passes: forced head moves, per-color reachability,
        empty-region checks, and degree-based forcing. Return False on contradiction.
        """
        if metrics is not None:
            ensure_keys(
                metrics,
                (
                    "propagations_calls",
                    "propagations_rounds",
                    "propagations_forced_moves",
                    "propagations_contradictions",
                    "propagations_degree_moves",
                ),
            )
            bump(metrics, "propagations_calls")

        while True:
            ok_reach, _ = Propagation._compute_color_reachability(board)
            if not ok_reach or not board.empty_regions_port_ok():
                if metrics is not None:
                    bump(metrics, "propagations_contradictions")
                return False

            forced_steps: list[tuple[Coord, Coord]] = []
            for head in board.active_heads():
                empties = [
                    nb for nb in board.neighbors(head) if nb != -1 and board.grid[nb] == -1
                ]
                legal_empties = [
                    cell for cell in empties if board.local_legal_after_paint(head, cell)
                ]
                if len(legal_empties) == 0:
                    if metrics is not None:
                        bump(metrics, "propagations_contradictions")
                    return False
                if len(legal_empties) == 1:
                    forced_steps.append((head, legal_empties[0]))

            changed = False
            applied = 0
            for head, cell in forced_steps:
                if board.grid[cell] != -1:
                    continue
                color = board.grid[head]
                board.paint(cell, color)
                applied += 1
                changed = True

            if metrics is not None and applied:
                bump(metrics, "propagations_forced_moves", applied)

            ok_degree, degree_changed = Propagation._force_degree_neighbors(board, metrics)
            if not ok_degree:
                return False
            changed = changed or degree_changed

            if changed:
                if metrics is not None:
                    bump(metrics, "propagations_rounds")

                if Propagation.any_color_disconnected(board) or Propagation.stranded_empty_exists(
                    board
                ):
                    if metrics is not None:
                        bump(metrics, "propagations_contradictions")
                    return False
                continue

            return True
