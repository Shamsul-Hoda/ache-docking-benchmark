# Benchmarking AutoDock Vina for acetylcholinesterase inhibitors

Can docking scores separate known AChE inhibitors from property-matched decoys, and is any separation explained by molecule size alone?

A fully scripted, reproducible virtual screening benchmark: protocol validation by redocking, screening of 1,219 compounds, and a size-bias control.

## Key results

| Metric | Value |
|---|---|
| Redocking validation (donepezil, R enantiomer) | **0.75 Å RMSD** (threshold: 2 Å) |
| Same with the S enantiomer | 3.14 Å (fail) |
| Compounds screened | 1,219 (40 actives, 1,179 decoys) |
| **ROC AUC** | **0.709** (95% CI 0.591–0.818) |
| **Enrichment factor, top 1%** | **15.2×** (6 actives in the top 12) |
| Enrichment factor, top 5% / 10% | 7.5× / 5.7× |
| Actives in the top 20 | 8 (0.7 expected by chance) |
| **Size-only baseline AUC** (heavy atom count, no docking) | **0.576** |
| Ligand efficiency ranking AUC | 0.572 |
| Correlation: score vs heavy atoms | r = −0.78 |

**Summary.** Vina ranked actives above decoys 71% of the time, with strong early enrichment: half of its top 12 predictions were experimentally confirmed inhibitors. Docking scores correlated strongly with molecular size, but ranking by size alone performed close to random (0.576), so the enrichment reflects structural recognition rather than a size artefact. Ligand efficiency, a common size correction, performed worse than the raw score.

## Figures

<p align="center">
  <img src="results/redock_pose_overlay.png" width="47%" alt="Redocking validation: crystal pose and Vina top pose">
  <img src="results/roc_curve.png" width="47%" alt="ROC curve, AUC 0.709">
</p>

**Left:** protocol validation. Crystallographic donepezil (grey) and Vina's top-ranked pose (yellow), RMSD 0.75 Å.
**Right:** screening performance across the full library.

<p align="center">
  <img src="results/score_vs_size.png" width="47%" alt="Docking score versus heavy atom count">
  <img src="results/top_active_vs_decoy.png" width="47%" alt="Top-ranked active and decoy in the AChE gorge">
</p>

**Left:** score versus molecular size (r = −0.78). Within any size range, actives still score better than decoys.
**Right:** the top-ranked active (orange) and top-ranked decoy (cyan) overlaid on crystallographic donepezil (green). Both span the gorge between Trp286 and Trp86, which explains why the scoring function cannot fully separate them.

## Methods

**Receptor.** PDB 4EY7, human acetylcholinesterase in complex with donepezil, X-ray 2.35 Å. Chain A protein retained (PyMOL), waters and heteroatoms removed, hydrogens added at pH 7.4 and converted to PDBQT (Open Babel, rigid receptor).

**Search box.** Centred on the centroid of the crystallographic donepezil (−14.108, −43.833, 27.670), 22 × 22 × 22 Å, covering the full gorge from the catalytic site to the peripheral site. Stored in `prep/vina_config.txt` and reused unchanged for every ligand.

**Protocol validation.** Donepezil was rebuilt from SMILES and redocked. The initial build had the S configuration while the crystal ligand is R; since Vina cannot invert a chiral centre, the correct enantiomer was specified explicitly. The R form reproduced the native pose at 0.75 Å RMSD, the S form at 3.14 Å, despite near-identical scores (−11.81 vs −11.77).

**Benchmark set.** DEKOIS 2.0 acetylcholinesterase set: 40 experimentally confirmed actives (BindingDB) and property-matched decoys (ZINC). Actives and decoys are matched on molecular weight, logP, hydrogen-bond donors and acceptors, rotatable bonds and formal charge.

**Ligand preparation.** SMILES to 3D with RDKit (ETKDGv3, seed 42), MMFF optimisation, PDBQT via Meeko. 1,219 of 1,221 compounds prepared successfully; 2 decoys failed 3D embedding and were excluded.

**Docking.** AutoDock Vina 1.2, exhaustiveness 8, 9 modes, seed 42. Each ligand docked independently into the same rigid receptor. Total: 4.9 hours on 12 CPU threads.

**Analysis.** ROC AUC with a 95% confidence interval from 2,000 bootstrap resamples; enrichment factors at 1%, 5% and 10%; size-bias control by ranking the library on heavy atom count and on molecular weight with no docking.

## Limitations

- **Decoys are assumed inactive, not measured.** High-scoring decoys may be scoring-function false positives or untested actives, so the reported AUC and enrichment values are lower bounds.
- **Only 40 actives**, giving a wide confidence interval (±0.11 AUC).
- **Single rigid holo receptor.** The 4EY7 pocket is shaped around donepezil, which may favour similar ligands (holo bias). Receptor flexibility and alternative structures were not explored.
- **Small actives are systematically missed.** Roughly 7 of the 40 actives are compact, tacrine-like molecules. Vina's scoring scales with contact count, so these score poorly despite genuine potency. This produces the long flat section in the ROC curve.
- **No explicit water, no covalent binders, approximate scoring** (error of a few kcal/mol).
- This DEKOIS copy contains 1,181 of the official 1,200 decoys.

## Repository structure

```
data/      input structures; DEKOIS set fetched by script (not committed)
prep/      prepared receptor and ligands, Vina configuration
scripts/   notebooks 01-05 and the preparation, docking and box-drawing scripts
results/   scores, rankings, metrics and figures
notes.md   dated project log
```

## Reproduce

```bash
conda env create -f environment.yml
conda activate ache-docking
bash scripts/get_dekois_ache.sh        # download the benchmark set
python scripts/prepare_ligands.py      # SMILES to PDBQT
python scripts/dock_ligands.py         # batch docking (resumable)
```

Then run the notebooks in `scripts/` in order. Random seeds are fixed throughout, so results are reproducible.

## Tools

RDKit, Meeko, AutoDock Vina 1.2, Open Babel, PyMOL (open-source), pandas, scikit-learn, matplotlib, JupyterLab. Exact versions in `environment.yml`.

## References

- Eberhardt J, Santos-Martins D, Tillack AF, Forli S. AutoDock Vina 1.2.0: new docking methods, expanded force field, and Python bindings. *J Chem Inf Model* 2021, 61, 3891-3898.
- Bauer MR, Ibrahim TM, Vogel SM, Boeckler FM. Evaluation and optimization of virtual screening workflows with DEKOIS 2.0. *J Chem Inf Model* 2013, 53, 1447-1462.
- Cheung J, et al. Structures of human acetylcholinesterase in complex with pharmacologically important ligands. *J Med Chem* 2012, 55, 10282-10286. (PDB 4EY7)
- Mysinger MM, Carchia M, Irwin JJ, Shoichet BK. Directory of Useful Decoys, Enhanced (DUD-E). *J Med Chem* 2012, 55, 6582-6594.

## Author

Shamsul Hoda, M.Sc. Biotechnology, IIT Roorkee.