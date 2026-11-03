"""Helper functions for the machine-learning extension to the AChE docking benchmark.

Convention used everywhere in this module: a higher value means "more likely to be
active". Vina scores are more negative when better, so they are passed in negated.
"""
import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import rdFingerprintGenerator
from rdkit.Chem.Scaffolds import MurckoScaffold
from sklearn.metrics import roc_auc_score

RDLogger.DisableLog("rdApp.*")          # keep notebook output readable

SEED = 42


# ---------------------------------------------------------------- features

def morgan_matrix(smiles_list, radius=2, n_bits=2048):
    """Morgan (circular) fingerprints as a 0/1 matrix, one row per molecule."""
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=radius, fpSize=n_bits)
    rows = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            raise ValueError(f"could not parse SMILES: {smi}")
        rows.append(np.array(gen.GetFingerprint(mol), dtype=np.uint8))
    return np.vstack(rows)


def murcko_scaffolds(smiles_list):
    """Bemis-Murcko scaffold SMILES for each molecule, used to group the CV folds."""
    out = []
    for n, smi in enumerate(smiles_list):
        scaffold = MurckoScaffold.MurckoScaffoldSmiles(smiles=smi)
        # acyclic molecules have no scaffold; give each its own group so they
        # cannot all pile into one fold
        out.append(scaffold if scaffold else f"acyclic_{n}")
    return out


# ---------------------------------------------------------------- metrics

def roc_auc_ci(y_true, score, n_boot=2000, seed=SEED):
    """ROC AUC with a bootstrap 95% confidence interval.

    Same procedure as the Vina benchmark in 05_analysis.ipynb: resample the
    compounds with replacement n_boot times and take the 2.5th and 97.5th
    percentiles of the resulting AUCs.
    """
    y_true = np.asarray(y_true)
    score = np.asarray(score, dtype=float)
    auc = roc_auc_score(y_true, score)

    rng = np.random.default_rng(seed)
    boot = []
    n = len(y_true)
    while len(boot) < n_boot:
        idx = rng.choice(n, size=n, replace=True)
        if y_true[idx].sum() == 0 or y_true[idx].sum() == len(idx):
            continue                     # a resample with only one class has no AUC
        boot.append(roc_auc_score(y_true[idx], score[idx]))
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return auc, lo, hi


def enrichment_factor(y_true, score, fraction):
    """Enrichment factor at the top `fraction` of the ranking.

    Returns (n_top, hits, expected, ef): how many compounds are in the top slice,
    how many of them are actives, how many would be expected by chance, and the ratio.
    """
    y_true = np.asarray(y_true)
    order = np.argsort(-np.asarray(score, dtype=float))   # best first
    n_top = max(1, int(round(len(y_true) * fraction)))
    hits = int(y_true[order[:n_top]].sum())
    expected = n_top * y_true.mean()
    ef = hits / expected if expected > 0 else np.nan
    return n_top, hits, expected, ef


def metric_row(name, y_true, score, fractions=(0.01, 0.05)):
    """One row of the comparison table: AUC with CI plus enrichment factors."""
    auc, lo, hi = roc_auc_ci(y_true, score)
    row = {"method": name, "AUC": round(auc, 3),
           "CI_low": round(lo, 3), "CI_high": round(hi, 3)}
    for f in fractions:
        n_top, hits, expected, ef = enrichment_factor(y_true, score, f)
        row[f"EF_{int(f * 100)}%"] = round(ef, 1)
        row[f"hits_top_{int(f * 100)}%"] = f"{hits}/{n_top}"
    return row


# ---------------------------------------------------------------- docked poses

def top_pose(pdbqt_path, name=None):
    """Rebuild the best-scoring Vina pose as an RDKit molecule.

    Meeko writes the original SMILES into the PDBQT as a REMARK and Vina keeps it,
    so the molecule can be rebuilt with correct bond orders and stereochemistry
    instead of guessing them from coordinates.
    """
    from meeko import PDBQTMolecule, RDKitMolCreate

    pmol = PDBQTMolecule.from_file(str(pdbqt_path), skip_typing=True)
    mols = RDKitMolCreate.from_pdbqt_mol(pmol, only_cluster_leads=False)
    if not mols or mols[0] is None:
        raise ValueError(f"could not rebuild molecule from {pdbqt_path}")

    mol = mols[0]
    out = Chem.Mol(mol)
    out.RemoveAllConformers()
    out.AddConformer(mol.GetConformer(0), assignId=True)   # conformer 0 = Vina mode 1
    if name:
        out.SetProp("_Name", name)
    return out


def load_receptor(pdb_path, fudge_factor=0.50, s_radius=2.0):
    """Load the protonated receptor as a ProLIF molecule.

    The PDB has no bond records, so MDAnalysis infers bonds from interatomic
    distances. The default sulfur radius makes the cutoff slightly shorter than a
    real C-S bond (1.81 A), which leaves every Met and Cys side chain broken, so
    sulfur is widened to 2.0 A.
    """
    import MDAnalysis as mda
    import prolif as plf

    u = mda.Universe(str(pdb_path))
    u.atoms.guess_bonds(fudge_factor=fudge_factor, vdwradii={"S": s_radius})
    return plf.Molecule.from_mda(u.atoms)


def ifp_matrix(sdf_path, receptor):
    """Interaction fingerprints for every pose in an SDF, as a 0/1 DataFrame.

    Columns are (residue, interaction type) pairs, for example ('TRP86.A',
    'PiStacking'). Rows are compounds, in the order they appear in the SDF.
    """
    import prolif as plf

    fp = plf.Fingerprint()
    fp.run_from_iterable(plf.sdf_supplier(str(sdf_path)), receptor, progress=True)
    df = fp.to_dataframe()
    df.columns = [f"{res}|{itype}" for _lig, res, itype in df.columns]
    return df.astype(np.uint8)
