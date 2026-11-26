"""I349 supplementary counts on the rebuilt files (cross-tabs only, no modelling)."""
import sys, math, ctypes, pandas as pd, numpy as np
try: ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
except Exception: pass
tr = lambda x: math.floor(x*10000)/10000
def h(p1, p2): return tr(abs(2*math.asin(math.sqrt(p1))-2*math.asin(math.sqrt(p2))))
a = pd.read_pickle(sys.argv[1]); f = a[a.cc]
print("== 2020 file ==")
y = f[f.HeartDisease == "Yes"]
print("HeartDisease=Yes", len(y), "| MI only", int(((y.CVDINFR4 == 1) & (y.CVDCRHD4 != 1)).sum()), "| CHD/angina only (no MI)", int(((y.CVDCRHD4 == 1) & (y.CVDINFR4 != 1)).sum()), "| both", int(((y.CVDINFR4 == 1) & (y.CVDCRHD4 == 1)).sum()))
print("share of positives without MI", tr(((y.CVDCRHD4 == 1) & (y.CVDINFR4 != 1)).mean()))
w = f._LLCPWT
print("weighted vs unweighted HeartDisease prevalence h", h(0.0855, 0.0648))
dup = f.duplicated(subset=[c for c in f.columns if c in ["HeartDisease","BMI","Smoking","AlcoholDrinking","Stroke","PhysicalHealth","MentalHealth","DiffWalking","Sex","AgeCategory","Race","Diabetic","PhysicalActivity","GenHealth","SleepTime","Asthma","KidneyDisease","SkinCancer"]], keep="first")
print("duplicate rows (distinct respondents, distinct SEQNO/state):", int(dup.sum()), "share", tr(dup.mean()), "| HeartDisease=Yes among duplicates", int((f[dup].HeartDisease == "Yes").sum()))
print("Race imputed rows", int((f._RACE == 9).sum() + f._RACE.isna().sum()), "Other pooled: NHPI", int((f._RACE == 5).sum()), "other", int((f._RACE == 6).sum()), "multiracial", int((f._RACE == 7).sum()))
b = pd.read_pickle(sys.argv[2]); g = b[b.cc]
print("== 2022 no_nans file ==")
mi = g[g.HadHeartAttack == "Yes"]; nmi = g[g.HadHeartAttack == "No"]
pa, pb = (mi.HadAngina == "Yes").mean(), (nmi.HadAngina == "Yes").mean()
print("HadAngina=Yes | MI=Yes", int((mi.HadAngina == "Yes").sum()), "/", len(mi), tr(pa), "| MI=No", int((nmi.HadAngina == "Yes").sum()), "/", len(nmi), tr(pb), "| Cohen h", h(pa, pb))
for c in ["ChestScan","HadStroke","DifficultyWalking","HadDiabetes"]:
    p1 = (mi[c].str.startswith("Yes")).mean(); p0 = (nmi[c].str.startswith("Yes")).mean()
    print(f" {c} Yes | MI=Yes {tr(p1)} | MI=No {tr(p0)} | Cohen h {h(p1, p0)}")
print("2020-definition positives (_MICHD=1) in no_nans", int((g._MICHD == 1).sum()), "| of which HadHeartAttack=No (angina/CHD only)", int(((g._MICHD == 1) & (g.HadHeartAttack == "No")).sum()),
      "share", tr(((g._MICHD == 1) & (g.HadHeartAttack == "No")).sum()/(g._MICHD == 1).sum()))
print("'Other race only, Non-Hispanic' composition (raw _RACE1):", g[g.RaceEthnicityCategory == "Other race only, Non-Hispanic"]._RACE1.value_counts().to_dict(), "(3 AIAN, 4 Asian, 5 NHPI)")
print("race DK/refused respondents dropped (RaceEthnicityCategory NaN)", int(b.RaceEthnicityCategory.isna().sum()), "| would be imputed in 2020-style _IMPRACE")
r = b[b._RACE1.between(1, 8)]
k = r.groupby("_RACE1").apply(lambda s: pd.Series({"n": len(s), "kept_unw": s.cc.mean(), "kept_w": np.average(s.cc, weights=s._LLCPWT)}))
print(k.to_string(float_format=lambda x: f"{tr(x):.4f}"))
print("Cohen h retained share across reported race groups (max-min): unweighted", h(k.kept_unw.max(), k.kept_unw.min()), "weighted", h(k.kept_w.max(), k.kept_w.min()))
print("age 13 vs age 8 retained (weighted)", h(0.5725, 0.4544), "| age max-min weighted", h(0.5776, 0.4544))
ck = b[b.CHECKUP1 == 8]
print("never-checkup respondents", len(ck), "all dropped from no_nans:", int(ck.cc.sum()) == 0, "| weighted share of adults", tr(ck._LLCPWT.sum()/b._LLCPWT.sum()))
dk = (b.PNEUVAC4 == 7) | (b.TETANUS1 == 7) | (b.LCSCTSC1 == 7) | (b.HIVTST7 == 7) | (b.CHECKUP1 == 8) | (b.COVIDPOS == 7)
for nm, m in (("with a DK/never answer", dk), ("without", ~dk)):
    s = b[m & b._AGEG5YR.between(1, 13)]
    print(f" respondents {nm}: n {int(m.sum())} age>=65 share {tr(s._AGEG5YR.between(10, 13).mean())} MI unweighted {tr(s[s.mi.notna()].mi.mean())} MI weighted {tr(np.average(s[s.mi.notna()].mi, weights=s[s.mi.notna()]._LLCPWT))}")
p1 = b[dk & b.mi.notna()].mi.mean(); p0 = b[~dk & b.mi.notna()].mi.mean(); print(" Cohen h MI prevalence DK vs non-DK (unweighted)", h(p1, p0))
