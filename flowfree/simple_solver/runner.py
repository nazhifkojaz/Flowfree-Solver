from .board import Board
from .solver import Solver

from pathlib import Path
import pandas as pd


def solve_puzzle(
    initial: str, expected: str, size: int, color_count: int
) -> str | None:
    board = Board.from_string(initial, size, size, color_count)
    solver = Solver(board=board, TIME_CAP=180)
    solution = solver.solve()
    ok = True if solution else None

    return {
        "solution": solution,
        "matched": (expected == solution) if ok else None,
        "stats": solver.get_stats(),
    }


parent_dir = Path(__file__).resolve().parents[2]
csv_path = parent_dir / "data/benchmark_puzzles.csv"

df = pd.read_csv(csv_path)

results = []

# iterate through df rows
for idx, row in enumerate(df.itertuples(index=False), start=1):
    size = int(row.BoardSize)
    color_count = int(row.ColorCount)
    initial = row.InitialPuzzle
    completed = row.CompletePuzzle

    print(f"solving {initial}")
    print(f"expecting {completed}")

    run_one = solve_puzzle(
        initial=initial, expected=completed, size=size, color_count=color_count
    )

    if run_one:
        print(f"solution: {run_one["solution"]}")
        print(run_one["stats"])
        # results.append(run_one)
        results.append(
            {
                "size": size,
                "color_count": color_count,
                "board_idx": row.board_idx,
                "tag": row.Tag,
                "initial": initial,
                "solution": run_one["solution"],
                "matched": run_one["matched"],
                **run_one["stats"],
            }
        )

# results_df = pd.DataFrame(results)
# results_df.to_csv(parent_dir / "data/simple_benchmark_result_3mins.csv", index=False)
# print(results_df.head())
