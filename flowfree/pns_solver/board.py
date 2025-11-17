import collections
from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Self

from flowfree.utils import string_to_tokens


@dataclass
class Board:
    width: int
    height: int
    grid: list[int]
    endpoints: dict[int, tuple[int, int]]
    n_colors: int
    _neighbors: list[tuple[int, int, int, int]] = field(default_factory=list, init=False)

    @classmethod
    def from_string(
        cls, puzzle: str, width: int, height: int, color_count: int
    ) -> Self:
        tokens = string_to_tokens(puzzle, width, height, color_count)
        if tokens is None:
            raise ValueError("Puzzle string structure mismatch")

        grid: list[int] = []
        pos_by_color: dict[int, list[int]] = collections.defaultdict(list)

        for idx, token in enumerate(tokens):
            if token.lower() == "x":
                grid.append(-1)
            else:
                color = int(token)
                grid.append(color)
                pos_by_color[color].append(idx)

        endpoints: dict[int, tuple[int, int]] = {}
        for color, cells in pos_by_color.items():
            if len(cells) != 2:
                raise ValueError(f"Color {color} must appear exactly twice (found {len(cells)})")
            endpoints[color] = (cells[0], cells[1])

        board = cls(width, height, grid, endpoints, max(pos_by_color.keys(), default=0))
        return board.with_neighbor_cache()

    @classmethod
    def from_puzzle(
        cls, puzzle: str, width: int, height: int, color_count: int
    ) -> Self:
        return cls.from_string(puzzle, width, height, color_count)

    def with_neighbor_cache(self) -> Self:
        total = self.width * self.height
        self._neighbors = []
        for idx in range(total):
            x, y = idx % self.width, idx // self.width
            left = idx - 1 if x > 0 else -1
            right = idx + 1 if x + 1 < self.width else -1
            up = idx - self.width if y > 0 else -1
            down = idx + self.width if y + 1 < self.height else -1
            self._neighbors.append((left, right, up, down))
        return self

    def clone(self) -> Self:
        clone_board = Board(
            self.width,
            self.height,
            self.grid.copy(),
            self.endpoints,
            self.n_colors,
        )
        clone_board._neighbors = self._neighbors
        return clone_board

    def neighbors(self, idx: int) -> Iterable[int]:
        left, right, up, down = self._neighbors[idx]
        if left != -1:
            yield left
        if right != -1:
            yield right
        if up != -1:
            yield up
        if down != -1:
            yield down

    def is_endpoint(self, idx: int, color: int | None = None) -> bool:
        col = self.grid[idx] if color is None else color
        if col <= 0:
            return False
        a, b = self.endpoints[col]
        return idx == a or idx == b

    def same_deg(self, idx: int) -> int:
        color = self.grid[idx]
        if color <= 0:
            return 0
        return sum(1 for nb in self.neighbors(idx) if self.grid[nb] == color)

    def extendable_head(self, idx: int) -> bool:
        color = self.grid[idx]
        if color <= 0:
            return False
        degree = self.same_deg(idx)
        max_degree = 1 if self.is_endpoint(idx, color) else 2
        if degree >= max_degree:
            return False
        return any(self.grid[nb] == -1 for nb in self.neighbors(idx))

    def active_heads(self) -> list[int]:
        heads: list[int] = []
        for idx, value in enumerate(self.grid):
            if value > 0 and self.extendable_head(idx):
                heads.append(idx)
        return heads

    def local_legal_after_paint(self, head: int, dst: int) -> bool:
        color = self.grid[head]
        head_deg_new = self.same_deg(head) + 1
        if self.is_endpoint(head, color):
            if head_deg_new > 1:
                return False
        else:
            if head_deg_new > 2:
                return False

        dst_deg_new = sum(1 for nb in self.neighbors(dst) if self.grid[nb] == color)
        if self.is_endpoint(dst, color):
            if dst_deg_new > 1:
                return False
        else:
            if dst_deg_new > 2:
                return False

        for nb in self.neighbors(dst):
            if self.grid[nb] == color:
                neighbor_deg = self.same_deg(nb)
                neighbor_limit = 1 if self.is_endpoint(nb, color) else 2
                if neighbor_deg + 1 > neighbor_limit:
                    return False
        return True

    def degree_ok_local(self, idx: int, after_color: int | None = None) -> bool:
        color = self.grid[idx] if after_color is None else after_color
        if color == -1:
            return True
        same = 0
        unassigned = 0
        for nb in self.neighbors(idx):
            val = self.grid[nb]
            if val == color:
                same += 1
            elif val == -1:
                unassigned += 1
        is_endpoint = idx in self.endpoints[color]
        limit = 1 if is_endpoint else 2
        if same > limit:
            return False
        if unassigned == 0:
            required = 1 if is_endpoint else 2
            if same != required:
                return False
        return True

    def empty_regions_port_ok(self) -> bool:
        total = self.width * self.height
        seen = [False] * total
        for idx in range(total):
            if self.grid[idx] != -1 or seen[idx]:
                continue
            ports = 0
            dq = deque([idx])
            seen[idx] = True
            while dq:
                cur = dq.popleft()
                for nb in self.neighbors(cur):
                    val = self.grid[nb]
                    if val == -1:
                        if not seen[nb]:
                            seen[nb] = True
                            dq.append(nb)
                    else:
                        ports += 1
            if ports <= 1:
                return False
        return True

    def bfs_reachable_same_or_empty(self, start: int, target: int, color: int) -> bool:
        seen = [False] * (self.width * self.height)
        dq = collections.deque([start])
        seen[start] = True
        while dq:
            current = dq.popleft()
            if current == target:
                return True
            for nxt in self.neighbors(current):
                if nxt == -1 or seen[nxt]:
                    continue
                if self.grid[nxt] == -1 or self.grid[nxt] == color:
                    seen[nxt] = True
                    dq.append(nxt)
        return False

    def is_solved(self) -> bool:
        if any(value == -1 for value in self.grid):
            return False
        for idx, value in enumerate(self.grid):
            if value <= 0:
                return False
            degree = self.same_deg(idx)
            limit = 1 if self.is_endpoint(idx, value) else 2
            if degree != limit:
                return False
        for color, (a, b) in self.endpoints.items():
            if not self.bfs_reachable_same_or_empty(a, b, color):
                return False
        return True

    def paint(self, dst: int, color: int) -> None:
        self.grid[dst] = color

    def legal_moves(self) -> list[tuple[int, int]]:
        moves: list[tuple[int, int]] = []
        heads = self.active_heads()
        heads.sort(
            key=lambda head: sum(1 for nb in self.neighbors(head) if self.grid[nb] == -1)
        )

        for head in heads:
            empties = [nb for nb in self.neighbors(head) if nb != -1 and self.grid[nb] == -1]
            color = self.grid[head]
            a, b = self.endpoints[color]
            other = b if head == a else a

            def manhattan(i: int, j: int) -> int:
                dx = abs((i % self.width) - (j % self.width))
                dy = abs((i // self.width) - (j // self.width))
                return dx + dy

            empties.sort(key=lambda cell: manhattan(cell, other))
            for empty in empties:
                if self.local_legal_after_paint(head, empty):
                    moves.append((head, empty))
        return moves
