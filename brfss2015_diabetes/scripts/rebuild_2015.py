"""Rebuild the UCI 891 / Kaggle 'Diabetes Health Indicators' file from raw BRFSS 2015 (LLCP2015.XPT) and compare.
Counts and prevalences only (no outcome modelling).
Usage: python -I -X utf8 rebuild_2015.py <LLCP2015.XPT> <uci data.csv> <kaggle dir> <out pickle>
Recode = Teboul's published Kaggle notebook as documented (each rule listed in RULES below)."""
import sys, math, ctypes, pandas as pd, numpy as np
try: ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
except Exception: pass
xpt, uci, kag, outp = sys.argv[1:5]
tr = lambda x: math.floor(x*10000)/10000 if x >= 0 else -math.floor(-x*10000)/10000
RAW = ["DIABETE3","_RFHYPE5","TOLDHI2","_CHOLCHK","_BMI5","SMOKE100","CVDSTRK3","_MICHD","_TOTINDA","_FRTLT1","_VEGLT1",
       "_RFDRHV5","HLTHPLN1","MEDCOST","GENHLTH","MENTHLTH","PHYSHLTH","DIFFWALK","SEX","_AGEG5YR","EDUCA","INCOME2",
       "_LLCPWT","_STSTR","_PSU","_STATE"]
parts = []
for ch in pd.read_sas(xpt, format="xport", encoding="latin1", chunksize=50000):
    parts.append(ch[RAW].copy())
raw = pd.concat(parts, ignore_index=True); del parts
print("raw respondents", len(raw))
for c in RAW[:22]:
    vc = raw[c].value_counts(dropna=False)
    if len(vc) <= 15: print(" raw", c, {("NaN" if pd.isna(k) else int(k)): int(v) for k, v in vc.sort_index().items()})
    else: print(" raw", c, "distinct", len(vc), "NaN", int(raw[c].isna().sum()))
d = raw.copy()
RULES = [
 ("Diabetes_012","DIABETE3","1->2 (diabetes); 2 (yes, only during pregnancy)->0; 3 (no)->0; 4 (prediabetes/borderline)->1; 7,9,NaN dropped"),
 ("HighBP","_RFHYPE5","1 (no)->0; 2 (yes)->1; 9 dropped"),
 ("HighChol","TOLDHI2","1->1; 2->0; 7,9,NaN dropped (NaN = cholesterol never checked, skip pattern)"),
 ("CholCheck","_CHOLCHK","1 (within 5 y)->1; 2 (not within 5 y)->0; 3 (never)->0; 9 dropped"),
 ("BMI","_BMI5","/100 then rounded to integer; NaN dropped"),
 ("Smoker","SMOKE100","1->1; 2->0; 7,9 dropped"),
 ("Stroke","CVDSTRK3","1->1; 2->0; 7,9 dropped"),
 ("HeartDiseaseorAttack","_MICHD","1->1; 2->0; NaN dropped"),
 ("PhysActivity","_TOTINDA","1->1; 2->0; 9 dropped"),
 ("Fruits","_FRTLT1","1->1; 2->0; 9,NaN dropped"),
 ("Veggies","_VEGLT1","1->1; 2->0; 9,NaN dropped"),
 ("HvyAlcoholConsump","_RFDRHV5","1 (no)->0; 2 (yes)->1; 9 dropped"),
 ("AnyHealthcare","HLTHPLN1","1->1; 2->0; 7,9 dropped"),
 ("NoDocbcCost","MEDCOST","1->1; 2->0; 7,9 dropped"),
 ("GenHlth","GENHLTH","1-5 kept; 7,9 dropped"),
 ("MentHlth","MENTHLTH","88->0; 1-30 kept; 77,99 dropped"),
 ("PhysHlth","PHYSHLTH","88->0; 1-30 kept; 77,99 dropped"),
 ("DiffWalk","DIFFWALK","1->1; 2->0; 7,9 dropped"),
 ("Sex","SEX","1 (male)->1; 2 (female)->0"),
 ("Age","_AGEG5YR","1-13 kept; 14 (dk/refused) dropped"),
 ("Education","EDUCA","1-6 kept; 9 dropped"),
 ("Income","INCOME2","1-8 kept; 77,99 dropped"),
]
for r in RULES: print("RULE", r[0], "<-", r[1], ":", r[2])
d["Diabetes_012"] = d.DIABETE3.map({1:2, 2:0, 3:0, 4:1})
d["HighBP"] = d._RFHYPE5.map({1:0, 2:1}); d["HighChol"] = d.TOLDHI2.map({1:1, 2:0}); d["CholCheck"] = d._CHOLCHK.map({1:1, 2:0, 3:0})
d["BMI"] = (d._BMI5/100).round(); d["Smoker"] = d.SMOKE100.map({1:1,2:0}); d["Stroke"] = d.CVDSTRK3.map({1:1,2:0})
d["HeartDiseaseorAttack"] = d._MICHD.map({1:1,2:0}); d["PhysActivity"] = d._TOTINDA.map({1:1,2:0}); d["Fruits"] = d._FRTLT1.map({1:1,2:0})
d["Veggies"] = d._VEGLT1.map({1:1,2:0}); d["HvyAlcoholConsump"] = d._RFDRHV5.map({1:0,2:1}); d["AnyHealthcare"] = d.HLTHPLN1.map({1:1,2:0})
d["NoDocbcCost"] = d.MEDCOST.map({1:1,2:0}); d["GenHlth"] = d.GENHLTH.where(d.GENHLTH.isin([1,2,3,4,5]))
for v, s in (("MentHlth","MENTHLTH"),("PhysHlth","PHYSHLTH")):
    x = d[s].replace({88:0}); d[v] = x.where(x.between(0,30))
d["DiffWalk"] = d.DIFFWALK.map({1:1,2:0}); d["Sex"] = d.SEX.map({1:1,2:0}); d["Age"] = d._AGEG5YR.where(d._AGEG5YR.between(1,13))
d["Education"] = d.EDUCA.where(d.EDUCA.between(1,6)); d["Income"] = d.INCOME2.where(d.INCOME2.between(1,8))
F = ["HighBP","HighChol","CholCheck","BMI","Smoker","Stroke","HeartDiseaseorAttack","PhysActivity","Fruits","Veggies","HvyAlcoholConsump",
     "AnyHealthcare","NoDocbcCost","GenHlth","MentHlth","PhysHlth","DiffWalk","Sex","Age","Education","Income"]
print("missing after recode per feature (all raw):", {f: int(d[f].isna().sum()) for f in ["Diabetes_012"]+F})
d["cc"] = d[["Diabetes_012"]+F].notna().all(axis=1)
cc = d[d.cc].copy()
print("complete cases", len(cc), "dropped", len(d)-len(cc), "share kept", tr(len(cc)/len(d)))
print("valid label (DIABETE3 1-4)", int(d.Diabetes_012.notna().sum()))
print("Diabetes_012 in complete cases", cc.Diabetes_012.value_counts().sort_index().to_dict())
print("DIABETE3 in complete cases", cc.DIABETE3.value_counts().sort_index().to_dict())
cc["Diabetes_binary"] = (cc.Diabetes_012 == 2).astype(int)
key = ["Diabetes_binary"]+F
def mset(df, k): return df[k].astype(int).value_counts()
def match(a, b, name):
    j = pd.concat([a.rename("a"), b.rename("b")], axis=1).fillna(0)
    m = np.minimum(j.a, j.b).sum()
    print(f"multiset match {name}: rows a {int(j.a.sum())} b {int(j.b.sum())} matched {int(m)} rate vs b {tr(m/j.b.sum())}",
          f"patterns {len(j)} identical-count patterns {int((j.a==j.b).sum())} abs row diff {int((j.a-j.b).abs().sum())}")
    return m/j.b.sum()
u = pd.read_csv(uci)
r_uci = match(mset(cc, key), mset(u, key), "rebuild vs UCI")
kb = pd.read_csv(kag + "/diabetes_binary_health_indicators_BRFSS2015.csv")
k3 = pd.read_csv(kag + "/diabetes_012_health_indicators_BRFSS2015.csv")
k5 = pd.read_csv(kag + "/diabetes_binary_5050split_health_indicators_BRFSS2015.csv")
print("kaggle binary rows", len(kb), "012 rows", len(k3), "5050 rows", len(k5))
print("kaggle 012 counts", k3.Diabetes_012.value_counts().sort_index().to_dict(), "5050 counts", k5.Diabetes_binary.value_counts().sort_index().to_dict())
match(mset(cc, key), mset(kb, key), "rebuild vs Kaggle binary")
match(mset(kb, key), mset(u, key), "Kaggle binary vs UCI")
cc["Diabetes_012i"] = cc.Diabetes_012.astype(int)
k3k = k3.rename(columns={"Diabetes_012":"Diabetes_012i"})
match(mset(cc, ["Diabetes_012i"]+F), mset(k3k, ["Diabetes_012i"]+F), "rebuild vs Kaggle 012 (3-class)")
j = pd.concat([mset(k5,key).rename("a"), mset(kb,key).rename("b")], axis=1).fillna(0)
print("5050 rows not contained in the Kaggle binary file", int((j.a-j.b).clip(lower=0).sum()))
for f in F:
    a = cc[f].astype(int).value_counts().sort_index(); b = u[f].astype(int).value_counts().sort_index()
    if not a.equals(b): print(" marginal differs", f, "rebuild-uci", (a.sub(b, fill_value=0)).astype(int).loc[lambda s: s != 0].to_dict())
# weighted prevalence with design-based (Taylor) SE, with-replacement PSU approximation; single-PSU strata contribute 0
def wprev(df, y):
    w = df._LLCPWT.values; yy = df[y].values.astype(float); p = (w*yy).sum()/w.sum()
    z = pd.DataFrame({"h": df._STSTR.values, "psu": df._PSU.values, "z": w*(yy-p)/w.sum()})
    t = z.groupby(["h","psu"]).z.sum().reset_index(); v = 0.0; lonely = 0
    for h, g in t.groupby("h"):
        n = len(g)
        if n < 2: lonely += 1; continue
        v += n/(n-1)*((g.z-g.z.mean())**2).sum()
    return p, math.sqrt(v), lonely
all_lab = d[d.Diabetes_012.notna()].copy(); all_lab["Diabetes_binary"] = (all_lab.Diabetes_012 == 2).astype(int)
all_lab["pre_or_dm"] = all_lab.Diabetes_012.isin([1,2]).astype(int); cc["pre_or_dm"] = cc.Diabetes_012.isin([1,2]).astype(int)
for nm, df in (("all valid-label respondents", all_lab), ("complete cases (published population)", cc)):
    for y in ("Diabetes_binary","pre_or_dm"):
        p, se, lo = wprev(df, y)
        print(f"{nm} n={len(df)} {y}: unweighted {tr(df[y].mean())} weighted {tr(p)} design SE {tr(se)} (single-PSU strata {lo})")
def h(p1, p2): return abs(2*math.asin(math.sqrt(p1))-2*math.asin(math.sqrt(p2)))
for g in ["Income","Education","Sex","Age"]:
    pw = cc.groupby(g).apply(lambda s: np.average(s.Diabetes_binary, weights=s._LLCPWT))
    pu = cc.groupby(g).Diabetes_binary.mean()
    print(g, "weighted prev", {int(k): tr(v) for k, v in pw.items()})
    print("   Cohen h weighted: lowest-vs-highest", tr(h(pw.iloc[0], pw.iloc[-1])), "max-min", tr(h(pw.max(), pw.min())),
          "| unweighted: lowest-vs-highest", tr(h(pu.iloc[0], pu.iloc[-1])), "max-min", tr(h(pu.max(), pu.min())))
keep = ["DIABETE3","Diabetes_012","cc","_LLCPWT","_STSTR","_PSU","_STATE"]+F
d[keep].to_pickle(outp)
print("saved", outp, "rows", len(d), "rebuild PASS" if r_uci >= 0.99 else "rebuild FAIL (<0.99)")
