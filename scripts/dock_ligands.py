"""Dock all prepared ligands into AChE (4EY7 chain A) with AutoDock Vina.

Usage (from the project folder):
    python scripts/dock_ligands.py 3     # test: dock the next 3 ligands only
    python scripts/dock_ligands.py       # dock all remaining ligands
Safe to stop with Ctrl+C and restart: ligands already in the scores file are skipped.
"""
import csv
import os
import subprocess
import sys
import time

import pandas as pd

RECEPTOR = "prep/receptor_A.pdbqt"
CONFIG = "prep/vina_config.txt"
LIGAND_DIR = "prep/ligands_pdbqt"
LIGAND_LOG = "prep/ligand_prep_log.csv"
POSE_DIR = "results/poses"
SCORES_CSV = "results/docking_scores.csv"


def best_score(out_file):
    """Return the mode 1 affinity from a Vina output file."""
    with open(out_file) as f:
        for line in f:
            if line.startswith("REMARK VINA RESULT:"):
                return float(line.split()[3])
    raise ValueError("no score found in " + out_file)


def main():
    os.makedirs(POSE_DIR, exist_ok=True)
    ligands = pd.read_csv(LIGAND_LOG)
    ligands = ligands[ligands["status"] == "ok"]

    first_run = not os.path.exists(SCORES_CSV)
    done = set() if first_run else set(pd.read_csv(SCORES_CSV)["id"])
    todo = ligands[~ligands["id"].isin(done)]
    if len(sys.argv) > 1:
        todo = todo.head(int(sys.argv[1]))
    print(len(done), "already docked,", len(todo), "to dock now")

    with open(SCORES_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if first_run:
            writer.writerow(["id", "label", "score", "seconds"])
        for n, row in enumerate(todo.itertuples(), start=1):
            ligand = os.path.join(LIGAND_DIR, row.id + ".pdbqt")
            out = os.path.join(POSE_DIR, row.id + "_out.pdbqt")
            start = time.time()
            result = subprocess.run(
                ["vina", "--receptor", RECEPTOR, "--ligand", ligand,
                 "--config", CONFIG, "--out", out],
                capture_output=True, text=True)
            seconds = round(time.time() - start, 1)
            if result.returncode != 0:
                print(row.id, "FAILED:", result.stderr.strip()[-200:])
                continue
            score = best_score(out)
            writer.writerow([row.id, row.label, score, seconds])
            f.flush()
            print(f"{n}/{len(todo)}  {row.id}  label={row.label}  score={score}  ({seconds} s)")


if __name__ == "__main__":
    main()
