from pathlib import Path

import pandas as pd

from . import solve_puzzle as pns_solve


def solve_entry(initial: str, expected: str, size: int, color_count: int) -> dict[str, object]:
    ok, solution, stats = pns_solve(
        initial, size, size, color_count, time_limit=180.0, max_nodes=200_000
    )
    return {
        "solution": solution if ok else None,
        "matched": (solution == expected) if ok else None,
        "stats": stats,
    }


def main(csv_path: Path | None = None) -> None:
    parent_dir = Path(__file__).resolve().parents[2]
    puzzles_path = csv_path or (parent_dir / "data/benchmark_puzzles.csv")
    df = pd.read_csv(puzzles_path)

    results = []
    for row in df.itertuples(index=False):
        size = int(row.BoardSize)
        initial = row.InitialPuzzle
        completed = row.CompletePuzzle

        print(f"solving {initial}")
        print(f"expecting {completed}")

        color_count = int(row.ColorCount)
        run = solve_entry(initial, completed, size, color_count)
        solution = run["solution"]
        print(f"solution: {solution}")
        print(run["stats"])

        results.append(
            {
                "size": size,
                "color_count": int(row.ColorCount),
                "board_idx": row.board_idx,
                "tag": row.Tag,
                "initial": initial,
                "solution": solution,
                "matched": run["matched"],
                **run["stats"],
            }
        )

    # Uncomment to persist results:
    results_df = pd.DataFrame(results)
    results_df.to_csv(parent_dir / "data/pns_benchmark_result_3mins.csv", index=False)
    print(results_df.head())


if __name__ == "__main__":
    main()
