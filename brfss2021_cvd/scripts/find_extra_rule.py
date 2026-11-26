"""I360: link rebuild rows to Kaggle rows by unique full tuples (H1), mark raw respondents kept vs dropped,
then scan every raw BRFSS 2021 variable for missingness/DK patterns that separate dropped from kept."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import zipfile, collections
import numpy as np, pandas as pd
W = WORK_ROOT + '/brfss2021_cvd/'
K = SURVEY_DATA_ROOT + '/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip'
XPT = SURVEY_DATA_ROOT + '/brfss/2021/xpt_unzipped/LLCP2021.XPT'
cc = pd.read_pickle(W + 'rebuild_h1_cc.pkl')
k = pd.read_csv(zipfile.ZipFile(K).open('CVD_cleaned.csv'))
cols = list(k.columns)
bt = cc[cols].round(2).astype(str).apply(tuple, axis=1)
kc = collections.Counter(k.round(2).astype(str).apply(tuple, axis=1))
bcount = collections.Counter(bt)
# a rebuild row is "kept" if its tuple is in Kaggle with the same multiplicity; "dropped" if tuple absent from Kaggle
status = pd.Series('ambiguous', index=cc.index)
status[bt.map(lambda t: kc.get(t, 0) == 0)] = 'dropped'
status[bt.map(lambda t: kc.get(t, 0) >= bcount[t])] = 'kept'
print(status.value_counts().to_dict())
status.to_pickle(W + 'link_status.pkl')
keep_idx = set(cc.index[status == 'kept']); drop_idx = set(cc.index[status == 'dropped'])
res = collections.defaultdict(lambda: [0, 0, 0, 0])  # missing_drop, n_drop, missing_keep, n_keep
off = 0
for ch in pd.read_sas(XPT, format='xport', chunksize=50000):
    ch.index = range(off, off + len(ch)); off += len(ch)
    d = ch.loc[ch.index.isin(drop_idx)]; kk = ch.loc[ch.index.isin(keep_idx)]
    for c in ch.columns:
        res[c][0] += int(d[c].isna().sum()); res[c][1] += len(d)
        res[c][2] += int(kk[c].isna().sum()); res[c][3] += len(kk)
rows = []
for c, (md, nd, mk, nk) in res.items():
    rows.append((c, md / nd if nd else 0, mk / nk if nk else 0))
t = pd.DataFrame(rows, columns=['var', 'miss_dropped', 'miss_kept'])
t['gap'] = t.miss_dropped - t.miss_kept
print(t.sort_values('gap', ascending=False).head(25).to_string(index=False))
t.to_csv(W + 'missing_gap.csv', index=False)
