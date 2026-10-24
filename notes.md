# Project notes
- 2026-10-16: Day 2. Created ache-docking conda env (conda-forge only), made project folders and README. Next: .gitignore, environment.yml, first commit.
- 2026-10-16: Day 2 done. Repo live on GitHub. Next: Day 3, RDKit basics in Jupyter.
- 2026-10-17: Day 3. RDKit basics: drew donepezil, calculated properties, compared 4 AChE drugs with a loop. Next: Day 4, file formats (PDB, SDF, PDBQT).
- 2026-10-18: Day 4. Downloaded 4EY7 (X-ray, 2.35 A). Found E20 (donepezil), NAG, FUC, EDO, NO3, 2 chains, no hydrogens. Saved crystal donepezil as PDB and SDF. Next: Day 5, Meeko and PDBQT.
- 2026-10-19: Day 5. Built protonated donepezil from SMILES (58 atoms, +1), 3D with ETKDG seed 42, MMFF minimised, Meeko to PDBQT (TORSDOF 6). Note: SMILES had no stereo; take stereo from crystal for redocking. Next: Day 6, first docking.
- Box centre (from crystal E20, chain A): x -14.108, y -43.833, z 27.670; size 22 x 22 x 22 A
- 2026-10-20: Day 6. Receptor chain A cleaned (PyMOL) and converted with obabel -xr -p 7.4 (5090 atoms in PDBQT). Box centre -14.108, -43.833, 27.670, size 22. First Vina run: mode 1 -11.77 kcal/mol, right location and orientation, benzyl ring differs; mode 4 (-11.18) closer to crystal. Next: Stage 3 redocking with correct stereo and RMSD.
- 2026-10-24: Redocking validated. R-donepezil top pose RMSD 0.75 A vs crystal (S form 3.14 A).
