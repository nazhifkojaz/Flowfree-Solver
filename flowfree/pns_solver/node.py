from dataclasses import dataclass, field
from typing import Self

from .board import Board


@dataclass
class Node:
    board: Board
    parent: Self | None = None
    children: list[Self] = field(default_factory=list)
    expanded: bool = False
    pn: int = 1
    dn: int = 1
    key: tuple[int, ...] = field(default_factory=tuple)
    depth: int = 0

    def compute_key(self) -> None:
        self.key = tuple(self.board.grid)
