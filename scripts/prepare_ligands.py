"""Prepare DEKOIS AChE ligands for docking: SMILES -> 3D -> PDBQT.

Usage (from the project folder):
    python scripts/prepare_ligands.py        # all molecules
    python scripts/prepare_ligands.py 5      # test run: first 5 only
"""
import os
import sys

import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem
from meeko import MoleculePreparation, PDBQTWriterLegacy

IN_CSV = "data/dekois_ache/ligands.csv"
OUT_DIR = "prep/ligands_pdbqt"
LOG_CSV = "prep/ligand_prep_log.csv"


def smiles_to_pdbqt(smiles):
    """Same recipe as donepezil: add H, 3D (ETKDGv3, seed 42), MMFF, Meeko."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError("SMILES could not be read")
    mol = Chem.AddHs(mol)

    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    if AllChem.EmbedMolecule(mol, params) != 0:
        params.useRandomCoords = True          # second try for hard molecules
        if AllChem.EmbedMolecule(mol, params) != 0:
            raise ValueError("3D embedding failed")
    AllChem.MMFFOptimizeMolecule(mol, maxIters=2000)

    setup = MoleculePreparation().prepare(mol)[0]
    pdbqt, ok, error = PDBQTWriterLegacy.write_string(setup)
    if not ok:
        raise ValueError(error)
    return pdbqt


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = pd.read_csv(IN_CSV)
    if len(sys.argv) > 1:
        df = df.head(int(sys.argv[1]))

    log = []
    for n, row in enumerate(df.itertuples(), start=1):
        out_file = os.path.join(OUT_DIR, row.id + ".pdbqt")
        try:
            with open(out_file, "w") as f:
                f.write(smiles_to_pdbqt(row.smiles))
            log.append((row.id, row.label, "ok", ""))
        except Exception as error:
            if os.path.exists(out_file):
                os.remove(out_file)
            log.append((row.id, row.label, "failed", str(error)))
        if n % 100 == 0:
            print(n, "molecules done")

    log = pd.DataFrame(log, columns=["id", "label", "status", "error"])
    log.to_csv(LOG_CSV, index=False)
    print(log["status"].value_counts())


if __name__ == "__main__":
    main()
