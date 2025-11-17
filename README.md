# Flowfree-Solver

This repository contains three FlowFree/Numberlink solvers, a benchmark suite and a dataset of flowfree puzzles (see `data/`). Solver included are:
- **python_port**: basic head-extending with Forward Checking (FC) + DFS.
- **improved_port**: improved `python_port` with stronger domain maintenance + FC + DFS + propagations + validators + transposition table (TT) + completed color pruning.
- **simple_solver**: reachability + propagation + DFS.


## Quick  result comparison (time cap: 3 minutes per puzzle)

| Solver        |   Total |   Solved |   Timed out |   Failed | Solve rate   |
|:--------------|--------:|---------:|------------:|---------:|:-------------|
| python_port   |      90 |        49 |          41 |       0 | 54.4%        |
| improved_port |      90 |        80 |          10 |       0 | 88.9%        |
| pns_solver    |      90 |        84 |           6 |       0 | 93.3%        |
| simple_solver |      90 |        90 |           0 |       0 | 100.0%       |

**Note:** see each solver's .md files and benchmark result data for detailed stats.

## Strcture
- `flowfree/`: where the solvers are located.
- `src_old/`: where the original C# solver implentation is located.
- `data/`: puzzle datasets and benchmark results.
- `result_analysis.ipynb`: Jupyter notebook for analyzing benchmark results (incomplete).

## Installation
Requires `Python 3.11+` (tested on 3.12) and `Poetry`.
```bash
git clone https://github.com/nazhifkojaz/Flowfree-Solver.git
cd Flowfree-Solver

# install dependencies in pyproject.toml
poetry install --no-root

# optional: activate the virtual environment
poetry shell
```

## Re-run benchmarks (on your local machine)
```bash
# locate to flowfree/ folder
cd flowfree/

# run benchmark script for selected solver
python3 -m simple_solver.runner
```
**Note:** the runners are hardcoded to run the full `benchmark_puzzles.csv` in `data/` folder with a 3-minute time cap per puzzle. Please do modify the script on your own if you want to change the dataset or time cap.
