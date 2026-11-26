"""Multiset row match of the Kaggle Flu Shot rows against the NHFS adult rebuild; month spread of matched and unmatched rows.
Usage: python -I -X utf8 match_k1.py"""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import os, psutil, collections
import numpy as np, pandas as pd
psutil.Process(os.getpid()).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
W = WORK_ROOT + '/nhfs2009_flu/'
K = SURVEY_DATA_ROOT + '/flushot-kaggle/raw/'
r = pd.read_pickle(W + 'k1_rebuild.pkl')
tr = pd.read_csv(K + 'training_set_features.csv'); te = pd.read_csv(K + 'test_set_features.csv')
lab = pd.read_csv(K + 'training_set_labels.csv')
tr = tr.merge(lab, on='respondent_id'); tr['_set'] = 'train'; te['_set'] = 'test'
k = pd.concat([tr, te], ignore_index=True)
plain = [c for c in te.columns if c not in ('respondent_id', 'hhs_geo_region', 'employment_industry', 'employment_occupation', '_set')]
def keys(df, cols):
    return [tuple('NA' if pd.isna(v) else v for v in row) for row in df[cols].itertuples(index=False)]
def t4(x): return int(x * 10000) / 10000
r['_key'] = keys(r, plain); k['_key'] = keys(k, plain)
rc = collections.Counter(r._key); kc = collections.Counter(k._key)
matched = sum(min(n, rc[key]) for key, n in kc.items())
print('kaggle rows', len(k), 'matched (features, multiset)', matched, 'rate', t4(matched / len(k)))
print('kaggle rows with no rebuild partner', len(k) - matched)
# training rows: features + labels
lc = plain + ['h1n1_vaccine', 'seasonal_vaccine']
r['_keyl'] = keys(r, lc); trk = keys(tr, lc); rcl = collections.Counter(r._keyl); tcl = collections.Counter(trk)
ml = sum(min(n, rcl[key]) for key, n in tcl.items())
print('train rows matched with labels', ml, 'rate', t4(ml / len(tr)))
# unique-key linkage: keys appearing once in rebuild and once in kaggle
uniq = {key for key, n in kc.items() if n == 1 and rc.get(key) == 1}
print('unique linked rows', len(uniq))
r['_in'] = r._key.map(lambda x: kc.get(x, 0) > 0)
# rebuild rows whose key never appears in kaggle = surely excluded
ex = r[~r._in]
print('rebuild adults whose features never appear in kaggle', len(ex))
mo = ['OCT09', 'NOV09', 'DEC09', 'JAN10', 'FEB10', 'MAR10', 'APR10', 'MAY10', 'JUN10']
print('\nmonth, adults, surely-excluded, share excluded')
for m in sorted(r.INT_MONTH.unique()):
    n = (r.INT_MONTH == m).sum(); e = (ex.INT_MONTH == m).sum()
    print(m, n, e, t4(e / n))
print('\nexcluded: label missing h1n1', ex.h1n1_vaccine.isna().sum(), 'seasonal', ex.seasonal_vaccine.isna().sum())
lk = r[r._key.isin(uniq)].copy()
kk = k[k._key.isin(uniq)].set_index('_key')
lk['_set'] = lk._key.map(kk._set)
print('\nunique-linked rows by month and set')
print(pd.crosstab(lk.INT_MONTH, lk._set))
# month of linked train rows with label
lt = lk[lk._set == 'train']
print('\nlinked train rows: h1n1 vaccinated share by interview month')
for m, g in lt.groupby('INT_MONTH'):
    print(m, len(g), t4(g.h1n1_vaccine.mean()))
# scrambled codes: bijection by linked rows
for raw, kag in [('_region', 'hhs_geo_region'), ('_ind', 'employment_industry'), ('_occ', 'employment_occupation')]:
    lk[kag] = lk._key.map(kk[kag])
    ct = pd.crosstab(lk[raw].fillna(-1), lk[kag].fillna('NA'))
    pure = (ct.gt(0).sum(axis=1) == 1).mean()
    print(f'\n{kag}: raw codes {ct.shape[0]}, kaggle codes {ct.shape[1]}, share of raw codes mapping to one kaggle code {t4(pure)}')
lk.to_pickle(W + 'k1_linked.pkl'); r.to_pickle(W + 'k1_rebuild_keyed.pkl')
