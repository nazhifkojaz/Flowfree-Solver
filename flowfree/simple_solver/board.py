from collections import defaultdict, deque
from dataclasses import dataclass
from ..utils import string_to_tokens

EMPTY = -1


@dataclass
class Cell:
    id: int
    value: int = EMPTY


class Board:
    def __init__(self, width: int, height: int, n_colors: int):
        self.width = width
        self.height = height
        self.n_colors = n_colors

        # total cells
        self.n = width * height

        # simplified cell/state structure
        self.cells: list[Cell] = [Cell(i, EMPTY) for i in range(self.n)]
        self.endpoints: dict[int, tuple[int, int]] = {}
        self.colors: list[int] = []

        # global neighborhood
        self.adj: list[list[int]] = [[] for _ in range(self.n)]
        self._init_adj()

        # simplified log for backtracking
        self._log: list[tuple[int, int]] = []  # (idx, old_value)

    @classmethod
    def from_string(
        cls,
        puzzle_str: str,
        width: int,
        height: int,
        color_count: int,  # required: colors 1..color_count
    ) -> "Board":
        """
        Parse puzzle string into a Board.
        x is empty, digits (1 ~ color_count) are colored endpoints.
        every color must appear twice (two endpoints rule guard)
        """

        tokens = string_to_tokens(puzzle_str, width, height, color_count)
        if tokens is None:
            print("Error in parsing the puzzle string")
            return cls(width, height, color_count)  # return empty board

        # Build the board and validate endpoints
        board = cls(width, height, color_count)
        seen = defaultdict(list)

        for idx, tok in enumerate(tokens):
            if tok != "x":
                c = int(tok)
                if not (1 <= c <= color_count):
                    raise ValueError(f"Color {c} out of bounds 1..{color_count}")
                board._set(idx, c)
                seen[c].append(idx)

        # Exactly two endpoints per color
        for c in range(1, color_count + 1):
            locs = seen.get(c, [])
            if len(locs) != 2:
                raise ValueError(
                    f"Color {c} must appear exactly twice (got {len(locs)})"
                )
            board.endpoints[c] = (locs[0], locs[1])

        # Construction bookkeeping
        board._log.clear()
        board.colors = list(range(1, color_count + 1))
        return board

    # global neighborhood/peers
    def _init_adj(self):
        for i in range(self.n):
            r, c = divmod(i, self.width)
            if r > 0:
                self.adj[i].append(i - self.width)
            if r < self.height - 1:
                self.adj[i].append(i + self.width)
            if c > 0:
                self.adj[i].append(i - 1)
            if c < self.width - 1:
                self.adj[i].append(i + 1)

    def neighbors(self, idx: int) -> list[int]:
        return self.adj[idx]

    def _set(self, idx: int, color: int) -> None:
        """
        Set cell to color (or EMPTY), bookkeeping for undos/backtracks.
        """
        old = self.cells[idx].value
        if old == color:
            return
        self._log.append((idx, old))
        self.cells[idx].value = color

    def push(self) -> int:
        """
        Mark a backtrack referencing point, return current log length.
        """
        return len(self._log)

    def pop(self, mark: int) -> None:
        """
        Undo/backtrack to referenced mark point.
        """
        while len(self._log) > mark:
            idx, old = self._log.pop()
            self.cells[idx].value = old

    def is_full(self) -> bool:
        return all(c.value != EMPTY for c in self.cells)

    def to_string(self) -> str:
        return "".join("x" if c.value == EMPTY else str(c.value) for c in self.cells)

    # dead-pocket / port test: every empty region must have >= 2 ports to colored cells
    def empty_regions_port_ok(self) -> bool:
        seen = [False] * self.n
        for i in range(self.n):
            if self.cells[i].value != EMPTY or seen[i]:
                continue
            ports = 0
            q = deque([i])
            seen[i] = True
            while q:
                u = q.popleft()
                for v in self.adj[u]:
                    val = self.cells[v].value
                    if val == EMPTY:
                        if not seen[v]:
                            seen[v] = True
                            q.append(v)
                    else:
                        ports += 1
            if ports <= 1:
                return False
        return True

    # Reachability for a color via {EMPTY ∪ color}
    def endpoints_reachable(self, color: int) -> bool:
        s, t = self.endpoints[color]
        allowed = (EMPTY, color)
        seen = [False] * self.n
        q = deque([s])
        seen[s] = True
        while q:
            u = q.popleft()
            if u == t:
                return True
            for v in self.adj[u]:
                if not seen[v] and self.cells[v].value in allowed:
                    seen[v] = True
                    q.append(v)
        return False

    def all_reachable(self) -> bool:
        return all(self.endpoints_reachable(c) for c in self.colors)

    # connectivity/degree check: endpoints must finish deg 1, internals deg 2.
    # added 'after_color' check for hypothetical coloring of an empty cell.
    def degree_ok_local(self, idx: int, after_color: int | None = None) -> bool:
        c = self.cells[idx].value if after_color is None else after_color
        if c == EMPTY:
            return True
        same = 0
        unassigned = 0
        for nb in self.adj[idx]:
            v = self.cells[nb].value
            if v == c:
                same += 1
            elif v == EMPTY:
                unassigned += 1
        is_endpoint = idx in self.endpoints[c]
        limit = 1 if is_endpoint else 2
        if same > limit:
            return False
        if unassigned == 0:
            required = 1 if is_endpoint else 2
            if same != required:
                return False
        return True
