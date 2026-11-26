"""Describe the adults absent from the Kaggle rows. Usage: python -I -X utf8 excl_k1.py"""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import os, psutil
import numpy as np, pandas as pd
psutil.Process(os.getpid()).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
W = WORK_ROOT + '/nhfs2009_flu/'
d = pd.read_pickle(W + 'nhfs_raw.pkl'); a = d[d.SUBGROUP == 'A']
r = pd.read_pickle(W + 'k1_rebuild_keyed.pkl')
def t4(x): return int(x * 10000) / 10000
ex = r[~r._in]; inn = r[r._in]
feat = [c for c in r.columns if not c.startswith('_') and c not in ('h1n1_vaccine', 'seasonal_vaccine', 'INT_MONTH', 'FLUWT', 'STATE')]
print('n excluded', len(ex), 'included', len(inn))
print('missing feature count: excluded mean', t4(ex[feat].isna().sum(axis=1).mean()), 'included mean', t4(inn[feat].isna().sum(axis=1).mean()))
print('either label missing: excluded', (ex.h1n1_vaccine.isna() | ex.seasonal_vaccine.isna()).sum(), 'included', (inn.h1n1_vaccine.isna() | inn.seasonal_vaccine.isna()).sum())
print('label rate h1n1 excluded', t4(ex.h1n1_vaccine.mean()), 'included', t4(inn.h1n1_vaccine.mean()))
for c in ['age_group', 'race', 'sex', 'census_msa']:
    print(c, (ex[c].value_counts(normalize=True).map(t4)).to_dict())
ra = a.loc[r.index]
for c in ['SAMP_DESIG', 'LANGUAGE', 'STATE']:
    e = ra.loc[ex.index, c].value_counts(); i = ra.loc[inn.index, c].value_counts()
    sh = (e / (e + i.reindex(e.index).fillna(0))).sort_values(ascending=False)
    print(c, 'excluded share by value (top)', sh.head(8).map(t4).to_dict(), ' zero-excluded values:', len(set(i.index) - set(e.index)))
# all excluded rows from a few states?
s = ra.loc[ex.index, 'STATE'].value_counts(); print('states with excluded rows', len(s), 'top', s.head(5).to_dict())
