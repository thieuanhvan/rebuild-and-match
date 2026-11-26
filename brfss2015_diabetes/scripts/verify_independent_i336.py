"""Independent re-check of the I336 core claims (written fresh, does not reuse rebuild_2015.py)."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import sys, hashlib, collections
import pandas as pd

K = SURVEY_DATA_ROOT + "/kaggle-diabetes-2015/"
UCI = SURVEY_DATA_ROOT + "/brfss/uci-891/data.csv"
XPT = SURVEY_DATA_ROOT + "/brfss/2015/xpt_unzipped/LLCP2015.XPT"

def t4(x):
    return int(x * 10000) / 10000

f012 = pd.read_csv(K + "diabetes_012_health_indicators_BRFSS2015.csv")
fbin = pd.read_csv(K + "diabetes_binary_health_indicators_BRFSS2015.csv")
f50 = pd.read_csv(K + "diabetes_binary_5050split_health_indicators_BRFSS2015.csv")
uci = pd.read_csv(UCI)
print("rows 012/bin/5050/uci:", len(f012), len(fbin), len(f50), len(uci))
print("012 counts:", f012.Diabetes_012.value_counts().sort_index().to_dict())
print("bin counts:", fbin.Diabetes_binary.value_counts().sort_index().to_dict())
print("5050 counts:", f50.Diabetes_binary.value_counts().sort_index().to_dict())
print("uci columns:", list(uci.columns)[:3], "... n cols", uci.shape[1])
ylab = [c for c in uci.columns if 'iabet' in c][0]
print("uci label", ylab, uci[ylab].value_counts().sort_index().to_dict())

feats = [c for c in f012.columns if c != 'Diabetes_012']
# (a) binary file == 012 file with 1->0, 2->1 (row order)
same_feats = (f012[feats].values == fbin[feats].values).all()
mapped = f012.Diabetes_012.map({0: 0, 1: 0, 2: 1}).values
print("bin rows aligned to 012 rows, features equal:", bool(same_feats), "| label == 012 mapped {1->0,2->1}:", bool((mapped == fbin.Diabetes_binary.values).all()))
print("prediabetes (012==1) rows with binary label 0:", int(((f012.Diabetes_012 == 1) & (fbin.Diabetes_binary == 0)).sum()))

# (b) 5050 class 1 rows: are they all 012 class-2 rows? multiset compare
def ms(df, cols):
    return collections.Counter(map(tuple, df[cols].values.tolist()))
c50_1 = ms(f50[f50.Diabetes_binary == 1], feats)
c012_2 = ms(f012[f012.Diabetes_012 == 2], feats)
c012_1 = ms(f012[f012.Diabetes_012 == 1], feats)
print("5050 class-1 multiset == 012 class-2 multiset:", c50_1 == c012_2)
print("5050 class-1 rows also matching a 012 prediabetes pattern (upper bound):", sum((c50_1 & c012_1).values()))

# (c) UCI vs Kaggle binary multiset (features + label)
ucif = [c for c in uci.columns if c in feats]
print("uci feature columns matched:", len(ucif), "of", len(feats))
if len(ucif) == len(feats):
    m1 = ms(uci.rename(columns={ylab: 'y'}), feats + ['y'])
    m2 = ms(fbin.rename(columns={'Diabetes_binary': 'y'}), feats + ['y'])
    print("uci == kaggle binary multiset:", m1 == m2)
print("duplicate rows in binary file (rows beyond first):", int(fbin.duplicated().sum()))

# (d) raw 2015
cols = ['DIABETE3', 'SEX', '_LLCPWT']
parts = []
for ch in pd.read_sas(XPT, format='xport', chunksize=50000):
    parts.append(ch[cols])
raw = pd.concat(parts)
print("raw respondents:", len(raw))
vc = raw.DIABETE3.value_counts(dropna=False).sort_index()
print("raw DIABETE3:", {(int(k) if k == k else 'NaN'): int(v) for k, v in vc.items()})
v = raw[raw.DIABETE3.isin([1, 2, 3, 4])]
w = v._LLCPWT
print("weighted prevalence code1 among codes 1-4:", t4((w * (v.DIABETE3 == 1)).sum() / w.sum()))
print("unweighted prevalence binary file:", t4(fbin.Diabetes_binary.mean()))
