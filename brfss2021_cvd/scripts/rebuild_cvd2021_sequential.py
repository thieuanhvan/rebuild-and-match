"""I360: test in-place sequential recoding of the consumption codes (each step applied to the already
modified column), all step orders, as a likely source of the Kaggle values."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import zipfile, collections, itertools
import numpy as np, pandas as pd
W = WORK_ROOT + '/brfss2021_cvd/'
K = SURVEY_DATA_ROOT + '/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip'
r = pd.read_pickle(W + 'raw2021_sub.pkl')
b0 = pd.read_pickle(W + 'rebuild_h1_all.pkl')
k = pd.read_csv(zipfile.ZipFile(K).open('CVD_cleaned.csv'))
kc = collections.Counter(map(tuple, k.round(2).astype(str).values.tolist()))

def step(v, name):
    v = v.copy()
    if name == 'day':
        m = (v >= 101) & (v <= 199); v[m] = (v[m] - 100) * 30
    elif name == 'week':
        m = (v >= 201) & (v <= 299); v[m] = (v[m] - 200) * 4
    elif name == 'month':
        m = (v >= 301) & (v <= 399); v[m] = v[m] - 300
    elif name == 'never':
        v[v == 555] = 0
    elif name == 'nan':
        v[v.isin([300, 777, 999])] = np.nan
    return v

best = None
for order in itertools.permutations(['day', 'week', 'month', 'never', 'nan']):
    b = b0.copy()
    for col, src in [('Fruit_Consumption', 'FRUIT2'), ('Green_Vegetables_Consumption', 'FVGREEN1'), ('FriedPotato_Consumption', 'FRENCHF1')]:
        v = r[src].astype(float)
        for s in order:
            v = step(v, s)
        b[col] = v
    cc = b.dropna()
    bc = collections.Counter(map(tuple, cc[k.columns].round(2).astype(str).values.tolist()))
    inter = sum((bc & kc).values())
    rate = int(inter / len(k) * 10000) / 10000
    if best is None or inter > best[1]:
        best = (order, inter, len(cc))
    if rate >= 0.999:
        print(order, 'complete', len(cc), 'matched', inter, 'rate', rate, 'exact' if (inter == len(k) == len(cc)) else '')
print('best', best)
