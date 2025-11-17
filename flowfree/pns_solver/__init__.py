from .board import Board
from .propagation import Propagation
from .solver import Solver

__all__ = ["Board", "Solver", "solve_puzzle"]


def solve_puzzle(
    puzzle: str,
    width: int,
    height: int,
    color_count: int,
    time_limit: float = 300.0,
    max_nodes: int = 200_000,
) -> tuple[bool, str, dict[str, int | float | bool]]:
    metrics: dict[str, int | float] = {}
    board = Board.from_puzzle(puzzle, width, height, color_count)
    if not Propagation.run(board, metrics):
        return False, "", {"reason": "contradiction after root propagation", **metrics}

    solver = Solver(
        board,
        NODE_CAP=max_nodes,
        TIME_CAP=time_limit,
        metrics=metrics,
    )
    solved, solved_board, stats = solver.solve()
    solution = ""
    if solved and solved_board is not None:
        solution = "".join(str(value) for value in solved_board.grid)
    return solved, solution, stats
