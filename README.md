# AChE Docking Benchmark

Benchmarking AutoDock Vina for identifying acetylcholinesterase (AChE) inhibitors.

## Aim

To test how well AutoDock Vina can tell known AChE inhibitors apart from similar-looking molecules that do not bind (DUD-E actives vs decoys).

## Status

Work in progress. Started October 2026.

## Repository structure

- `data/` raw input files (protein structure, DUD-E molecule sets)
- `prep/` prepared receptor and ligand files
- `scripts/` Python code for preparation, docking and analysis
- `results/` docking scores, plots and figures

## Tools

Python 3.11, RDKit, Meeko, Open Babel, AutoDock Vina, pandas, matplotlib, scikit-learn
