# Project notes
- 2026-10-16: Day 2. Created ache-docking conda env (conda-forge only), made project folders and README. Next: .gitignore, environment.yml, first commit.
- 2026-10-16: Day 2 done. Repo live on GitHub. Next: Day 3, RDKit basics in Jupyter.
- 2026-10-17: Day 3. RDKit basics: drew donepezil, calculated properties, compared 4 AChE drugs with a loop. Next: Day 4, file formats (PDB, SDF, PDBQT).
- 2026-10-18: Day 4. Downloaded 4EY7 (X-ray, 2.35 A). Found E20 (donepezil), NAG, FUC, EDO, NO3, 2 chains, no hydrogens. Saved crystal donepezil as PDB and SDF. Next: Day 5, Meeko and PDBQT.
- 2026-10-19: Day 5. Built protonated donepezil from SMILES (58 atoms, +1), 3D with ETKDG seed 42, MMFF minimised, Meeko to PDBQT (TORSDOF 6). Note: SMILES had no stereo; take stereo from crystal for redocking. Next: Day 6, first docking.
