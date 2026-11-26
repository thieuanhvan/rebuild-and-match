"""I360 final rebuild of CVD_cleaned.csv (alphiree, Kaggle) from raw BRFSS 2021 LLCP.
Consumption items (FRUIT2, FVGREEN1, FRENCHF1), recoded IN PLACE in this order:
  1) 300 (less than once a month), 777, 999 -> NaN
  2) 101-199 (per day)   -> (x-100)*30
  3) 201-299 (per week)  -> (x-200)*4
  4) 300-399 (per month) -> x-300   (also hits values created by steps 2-3)
  5) 555 (never)         -> 0
Then rows with any consumption value > CAP are dropped (CAP tested), rows with PHYSHLTH or MENTHLTH
in {77, 99} or missing are dropped (columns not in the file), Sex = _SEX, complete cases over 19 columns.
Usage: python -I -X utf8 rebuild_cvd2021_final.py"""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import zipfile, collections
import numpy as np, pandas as pd
W = WORK_ROOT + '/brfss2021_cvd/'
K = SURVEY_DATA_ROOT + '/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip'
r = pd.read_pickle(W + 'raw2021_sub.pkl'); ph = pd.read_pickle(W + 'raw2021_physment.pkl')
b0 = pd.read_pickle(W + 'rebuild_h1_all.pkl')
k = pd.read_csv(zipfile.ZipFile(K).open('CVD_cleaned.csv'))
kc = collections.Counter(map(tuple, k.round(2).astype(str).values.tolist()))
F = {'Fruit_Consumption': 'FRUIT2', 'Green_Vegetables_Consumption': 'FVGREEN1', 'FriedPotato_Consumption': 'FRENCHF1'}

def seq(s):
    v = s.astype(float).copy()
    v[v.isin([300, 777, 999])] = np.nan
    m = (v >= 101) & (v <= 199); v[m] = (v[m] - 100) * 30
    m = (v >= 201) & (v <= 299); v[m] = (v[m] - 200) * 4
    m = (v >= 300) & (v <= 399); v[m] = v[m] - 300
    v[v == 555] = 0
    return v

b = b0.copy(); b['Sex'] = r._SEX.map({1: 'Male', 2: 'Female'})
for c, s in F.items():
    b[c] = seq(r[s])
phok = ~(ph.isin([77, 99]).any(axis=1) | ph.isna().any(axis=1))
for cap in [None, 120, 128]:
    ok = phok.copy()
    if cap is not None:
        ok &= ~(b[list(F)] > cap).any(axis=1)
    cc = b[ok].dropna()
    bc = collections.Counter(map(tuple, cc[k.columns].round(2).astype(str).values.tolist()))
    inter = sum((bc & kc).values())
    print(f'cap {cap}: rows {len(cc)}, matched {inter}, only Kaggle {len(k) - inter}, only rebuild {len(cc) - inter}, exact {bc == kc}')
    if bc == kc:
        cc.to_pickle(W + 'rebuild_exact_cc.pkl')
