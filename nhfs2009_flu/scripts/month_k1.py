"""Label shares by interview month (linked training rows) and missingness by month (file population). Usage: python -I -X utf8 month_k1.py"""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import pandas as pd
W = WORK_ROOT + '/nhfs2009_flu/'
def t4(x): return int(x * 10000) / 10000
mo = ['OCT09', 'NOV09', 'DEC09', 'JAN10', 'FEB10', 'MAR10', 'APR10', 'MAY10', 'JUN10']
lk = pd.read_pickle(W + 'k1_linked.pkl'); lt = lk[lk._set == 'train']
print('linked training rows', len(lt))
for tgt in ('h1n1_vaccine', 'seasonal_vaccine'):
    print(tgt, {m: t4(lt[lt.INT_MONTH == m][tgt].mean()) for m in mo})
r = pd.read_pickle(W + 'k1_rebuild_keyed.pkl'); f = r[r._in]
print('file population', len(f))
for c in ('health_insurance', 'doctor_recc_h1n1'):
    print(c, 'missing', {m: t4(f[f.INT_MONTH == m][c].isna().mean()) for m in mo})
for tgt in ('h1n1_vaccine', 'seasonal_vaccine'):
    print(tgt, 'file population unweighted', t4(f[tgt].mean()))
