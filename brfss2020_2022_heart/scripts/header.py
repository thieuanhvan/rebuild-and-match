import sys, pandas as pd
for f in sys.argv[1:]:
    it = pd.read_sas(f, format="xport", encoding="latin1", chunksize=5)
    ch = next(it); print(f, len(ch.columns)); print(" ".join(ch.columns))
