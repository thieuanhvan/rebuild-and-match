"""Task 6: scrambled string <-> raw code on uniquely linked rows; plus a look at fully-absent adults."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nhfs_parse as P
import rebuild as R

P.lower_priority()
lay, recs = P.read()
adults = [r for r in recs if r["SUBGROUP"] == "A"]
tr, te, labd, key = R.load_pub()
pub = tr + te
A = collections.defaultdict(list)
for r in adults:
    A[R.rebuild(r)].append(r)
Pk = collections.defaultdict(list)
for p in pub:
    Pk[key(p)].append(p)
links = [(A[k][0], Pk[k][0]) for k in Pk if len(Pk[k]) == 1 and len(A.get(k, [])) == 1]
lines = [f"Task 6: uniquely linked rows (feature tuple occurs exactly once among adults and once among published) = {len(links)}"]
for raw, col in (("HHS_REGION", "hhs_geo_region"), ("Q95_INDSTR", "employment_industry"), ("Q95_OCCPN", "employment_occupation")):
    pairs = collections.Counter((r[raw], p[col] or "<blank>") for r, p in links)
    code2s = collections.defaultdict(set)
    s2code = collections.defaultdict(set)
    for (c, s), n in pairs.items():
        code2s[c].add(s)
        s2code[s].add(c)
    multi_c = {c: v for c, v in code2s.items() if len(v) > 1}
    multi_s = {s: v for s, v in s2code.items() if len(v) > 1}
    lines.append(f"  {col} <- {raw}: distinct raw codes = {len(code2s)}, distinct strings = {len(s2code)}; "
                 f"codes mapping to >1 string = {len(multi_c)}; strings mapping to >1 code = {len(multi_s)}")
    for c in sorted(code2s, key=lambda x: (x is None, x if x is not None else 0)):
        lines.append(f"    {c} -> {sorted(code2s[c])}  (n={sum(n for (cc, s), n in pairs.items() if cc == c)})")

# diagnostics on adults in feature groups that have no published row at all (fully identifiable absent)
gone = [r for k, rs in A.items() if k not in Pk for r in rs]
lines.append(f"Absent diagnostic: adults in feature groups with zero published rows = {len(gone)}")
for v in ("INT_MONTH", "SAMP_DESIG", "LANGUAGE", "AGEGRP", "VACC_H1N1_F", "VACC_SEAS_F"):
    c_g = collections.Counter(r[v] for r in gone)
    lines.append(f"  {v}: {sorted(c_g.items(), key=lambda x: str(x[0]))}")
allm = collections.Counter(r["INT_MONTH"] for r in adults)
lines.append(f"  all adults INT_MONTH: {sorted(allm.items(), key=lambda x: str(x[0]))}")
open(R.OUT + "scrambled_out.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
