"""Read the NHFS 2009-10 public-use fixed-width file using the column layout in nhfspuf.sas; save a pickle.
Usage: python -I -X utf8 read_nhfs.py"""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import re, os, psutil
import pandas as pd
psutil.Process(os.getpid()).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
R = SURVEY_DATA_ROOT + '/nhfs-2009/raw/'
W = WORK_ROOT + '/nhfs2009_flu/'
sas = open(R + 'nhfspuf.sas', encoding='latin-1').read()
block = sas[sas.index('INPUT'):]
block = block[:block.index(';')]
spec = re.findall(r'@(\d+)\s+(\w+)\s+(\$?)(\d+)\.(\d*)', block)
colspecs = [(int(p) - 1, int(p) - 1 + int(w)) for p, n, d, w, dec in spec]
names = [n for p, n, d, w, dec in spec]
char = {n for p, n, d, w, dec in spec if d}
df = pd.read_fwf(R + 'nhfspuf.dat', colspecs=colspecs, names=names, dtype={n: str for n in names}, header=None)
for n in names:
    if n not in char:
        df[n] = pd.to_numeric(df[n], errors='coerce')
df.to_pickle(W + 'nhfs_raw.pkl')
print(df.shape, 'columns', len(names))
print(df.INT_MONTH.value_counts().sort_index().to_dict())
# value labels block (PROC FORMAT) for later reading
open(W + 'nhfs_formats.txt', 'w', encoding='utf8').write(sas[:sas.index('INPUT')])
