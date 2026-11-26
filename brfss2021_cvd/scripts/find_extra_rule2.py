"""I360: after the sequential recode + cap 128, find raw codes present in dropped rows but never in kept rows."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import zipfile, collections
import numpy as np, pandas as pd
W = WORK_ROOT + '/brfss2021_cvd/'
K = SURVEY_DATA_ROOT + '/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip'
XPT = SURVEY_DATA_ROOT + '/brfss/2021/xpt_unzipped/LLCP2021.XPT'
cc = pd.read_pickle(W + 'rebuild_seq_cc.pkl')
F = ['Fruit_Consumption', 'Green_Vegetables_Consumption', 'FriedPotato_Consumption']
cc = cc[~(cc[F] > 128).any(axis=1)]
k = pd.read_csv(zipfile.ZipFile(K).open('CVD_cleaned.csv'))
cols = list(k.columns)
bt = cc[cols].round(2).astype(str).apply(tuple, axis=1)
kc = collections.Counter(k.round(2).astype(str).apply(tuple, axis=1)); bcount = collections.Counter(bt)
drop = set(cc.index[bt.map(lambda t: kc.get(t, 0) == 0)]); keep = set(cc.index[bt.map(lambda t: kc.get(t, 0) >= bcount[t])])
print('dropped', len(drop), 'kept', len(keep))
cnt_d = collections.Counter(); cnt_k = collections.Counter()
off = 0
for ch in pd.read_sas(XPT, format='xport', chunksize=50000):
    ch.index = range(off, off + len(ch)); off += len(ch)
    d = ch.loc[ch.index.isin(drop)]; kk = ch.loc[ch.index.isin(keep)]
    for c in ch.columns:
        if ch[c].dtype == object: continue
        for v, n in d[c].fillna(-1).value_counts().items(): cnt_d[(c, v)] += n
        for v, n in kk[c].fillna(-1).value_counts().items(): cnt_k[(c, v)] += n
rows = []
for (c, v), n in cnt_d.items():
    if cnt_k.get((c, v), 0) == 0 and n >= 50:
        rows.append((c, v, n, n / len(drop)))
t = pd.DataFrame(rows, columns=['var', 'code', 'n_dropped', 'share_dropped']).sort_values('n_dropped', ascending=False)
print(t.head(30).to_string(index=False))
t.to_csv(W + 'codes_only_in_dropped.csv', index=False)
