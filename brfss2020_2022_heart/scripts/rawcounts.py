import sys, pandas as pd
d = pd.read_pickle(sys.argv[1]); print(sys.argv[1], d.shape)
for c in d.columns:
    vc = d[c].value_counts(dropna=False)
    if len(vc) <= 16: print(c, {("NaN" if pd.isna(k) else (int(k) if float(k).is_integer() else k)): int(v) for k, v in vc.sort_index().items()})
    else: print(c, "distinct", len(vc), "NaN", int(d[c].isna().sum()))
