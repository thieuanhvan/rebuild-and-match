"""Extract selected raw BRFSS columns to a pickle. Usage: python -I -X utf8 extract.py <XPT> <out.pkl> <col> [col...]"""
import sys, ctypes, pandas as pd
try: ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
except Exception: pass
xpt, outp, cols = sys.argv[1], sys.argv[2], sys.argv[3:]
parts = []
for ch in pd.read_sas(xpt, format="xport", encoding="latin1", chunksize=50000):
    parts.append(ch[[c for c in cols if c in ch.columns]].copy())
d = pd.concat(parts, ignore_index=True); d.to_pickle(outp); print(xpt, d.shape, "missing cols", [c for c in cols if c not in d.columns])
