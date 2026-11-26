import sys, pandas as pd
for f in sys.argv[1:]:
    d = pd.read_csv(f)
    print("=====", f, d.shape)
    for c in d.columns:
        vc = d[c].value_counts(dropna=False)
        if len(vc) <= 30: print(c, vc.to_dict())
        else: print(c, "distinct", len(vc), "NaN", int(d[c].isna().sum()), "min", d[c].min(), "max", d[c].max(), "head", list(vc.index[:8]))
