"""Five-split median [range] AUCs for K1 Q1 (same splits, models and features as a4_k1.py) and weighted label shares.
Usage: python -I -X utf8 a4_k1_summary.py"""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_v] = '1'
import io, contextlib, runpy
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a4_k1.py'))
T, SPLITS, t4 = g['T'], g['SPLITS'], g['t4']
num, cat, feats = g['num'], g['cat'], g['feats']
for tgt in ('h1n1_vaccine', 'seasonal_vaccine'):
    for model, pa_, pb_ in (('lr', g['lr_pair'](num, cat), g['lr_pair'](num, cat + ['INT_MONTH'])),
                            ('lgb', g['lgb_pair'](feats), g['lgb_pair'](feats + ['INT_MONTH']))):
        A, B = [], []
        for i, j in SPLITS:
            a, b = T.iloc[i], T.iloc[j]
            Atr, Ate = pa_(a, b); Btr, Bte = pb_(a, b)
            A.append(roc_auc_score(b[tgt], g['predict'](model, Atr, a[tgt].values, Ate)))
            B.append(roc_auc_score(b[tgt], g['predict'](model, Btr, a[tgt].values, Bte)))
        print(f'{tgt} {model}: features {t4(np.median(A))} [{t4(min(A))}, {t4(max(A))}]; + INT_MONTH {t4(np.median(B))} [{t4(min(B))}, {t4(max(B))}]')

W = WORK_ROOT + '/nhfs2009_flu/'
r = pd.read_pickle(W + 'k1_rebuild_keyed.pkl')
for tgt in ('h1n1_vaccine', 'seasonal_vaccine'):
    v = r[r[tgt].notna()]
    f = v[v._in]
    wm = lambda d: (d[tgt] * d.FLUWT).sum() / d.FLUWT.sum()
    print(f'{tgt}: weighted all adults with valid label (n={len(v)}) {t4(wm(v))}; weighted file population (n={len(f)}) {t4(wm(f))}; unweighted file population {t4(f[tgt].mean())}')
print('adults with either label missing', int((r.h1n1_vaccine.isna() | r.seasonal_vaccine.isna()).sum()),
      '; of them with feature key in file', int(((r.h1n1_vaccine.isna() | r.seasonal_vaccine.isna()) & r._in).sum()))
print('rebuild adults', len(r), 'children in raw file', 70944 - len(r))
