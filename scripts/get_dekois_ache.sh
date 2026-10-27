#!/bin/bash
# Download DEKOIS 2.0 (Zenodo record 8131256) and extract the AChE set into data/dekois_ache/
set -e
mkdir -p ~/datasets data/dekois_ache
[ -f ~/datasets/DEKOIS2.zip ] || wget "https://zenodo.org/records/8131256/files/DEKOIS2.zip?download=1" -O ~/datasets/DEKOIS2.zip
python -c "import zipfile, os; z = zipfile.ZipFile(os.path.expanduser('~/datasets/DEKOIS2.zip')); [z.extract('DEKOIS2/ache/' + f, os.path.expanduser('~/datasets')) for f in ['active_decoys.smi', 'protein/ache_protein.pdb', 'protein/ache_ligand.mol2']]"
cp ~/datasets/DEKOIS2/ache/active_decoys.smi ~/datasets/DEKOIS2/ache/protein/ache_* data/dekois_ache/
echo "Actives: $(grep -c ' BDB' data/dekois_ache/active_decoys.smi)  Decoys: $(grep -c ' ZINC' data/dekois_ache/active_decoys.smi)"
