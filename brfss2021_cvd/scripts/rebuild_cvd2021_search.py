"""I360: search over conversion hypotheses for the three consumption items; report complete-case count
and multiset match against CVD_cleaned.csv."""
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

def cons(s, day, wk, mo, v300, v555):
    out = pd.Series(np.nan, index=s.index)
    d = (s > 100) & (s < 200); w = (s > 200) & (s < 300); m = (s > 300) & (s < 400)
    out[d] = day(s[d] - 100); out[w] = wk(s[w] - 200); out[m] = mo(s[m] - 300)
    if v300 is not None: out[s == 300] = v300
    if v555 is not None: out[s == 555] = v555
    return out

H = {
 'H1 d*30 w*4 m 300->0 555->0': (lambda x: x * 30, lambda x: x * 4, lambda x: x, 0, 0),
 'H2 555->NaN': (lambda x: x * 30, lambda x: x * 4, lambda x: x, 0, None),
 'H3 300->NaN': (lambda x: x * 30, lambda x: x * 4, lambda x: x, None, 0),
 'H4 300,555->NaN': (lambda x: x * 30, lambda x: x * 4, lambda x: x, None, None),
}
for name, (day, wk, mo, v300, v555) in H.items():
    b = b0.copy()
    for col, src in [('Fruit_Consumption', 'FRUIT2'), ('Green_Vegetables_Consumption', 'FVGREEN1'), ('FriedPotato_Consumption', 'FRENCHF1')]:
        b[col] = cons(r[src], day, wk, mo, v300, v555)
    cc = b.dropna()
    bc = collections.Counter(map(tuple, cc[k.columns].round(2).astype(str).values.tolist()))
    inter = sum((bc & kc).values())
    print(f'{name}: complete {len(cc)}, matched {inter}, match rate {int(inter / len(k) * 10000) / 10000}')

def cons5(s, cap):
    out = cons(s, lambda x: x * 30, lambda x: x * 4, lambda x: x, None, 0)
    out[(s > 100 + cap) & (s < 200)] = np.nan
    return out
for cap in [4]:
    b = b0.copy()
    for col, src in [('Fruit_Consumption', 'FRUIT2'), ('Green_Vegetables_Consumption', 'FVGREEN1'), ('FriedPotato_Consumption', 'FRENCHF1')]:
        b[col] = cons5(r[src], cap)
    cc = b.dropna()
    bc = collections.Counter(map(tuple, cc[k.columns].round(2).astype(str).values.tolist()))
    inter = sum((bc & kc).values())
    print(f'H5 300->NaN, day>{cap}/day->NaN: complete {len(cc)}, matched {inter}, match rate {int(inter / len(k) * 10000) / 10000}')
    cc.to_pickle(W + 'rebuild_h5_cc.pkl')
