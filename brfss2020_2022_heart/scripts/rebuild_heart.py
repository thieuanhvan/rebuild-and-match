"""I349: rebuild the Kaggle 'Personal Key Indicators of Heart Disease' files (kamilpytlak) from raw BRFSS and audit them.
Counts and prevalences only (no outcome modelling). Numbers truncated to 4 decimals.
Usage: python -I -X utf8 rebuild_heart.py <year 2020|2022> <raw pickle from extract.py> <kaggle dir (unzipped archive)> <out pickle>
Recode rules were inferred from the Kaggle column names/levels and the raw BRFSS codebooks; each is printed as RULE."""
import sys, math, ctypes, pandas as pd, numpy as np
try: ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
except Exception: pass
year, rawp, kag, outp = sys.argv[1:5]
tr = lambda x: math.floor(x*10000)/10000 if x >= 0 else -math.floor(-x*10000)/10000
raw = pd.read_pickle(rawp); d = raw.copy(); print("raw respondents", len(d))
YN = {1: "Yes", 2: "No"}
def yn(c): return d[c].map(YN)
def days(c):
    x = d[c].replace({88: 0}); return x.where(x.between(0, 30))
AGE = ["18-24","25-29","30-34","35-39","40-44","45-49","50-54","55-59","60-64","65-69","70-74","75-79","80 or older"]
GH = {1: "Excellent", 2: "Very good", 3: "Good", 4: "Fair", 5: "Poor"}
RULES = []
def R(col, src, txt): RULES.append((col, src, txt))
if year == "2020":
    d["HeartDisease"] = d._MICHD.map(YN); R("HeartDisease", "_MICHD", "1->Yes (CVDINFR4=1 or CVDCRHD4=1); 2->No (both=2); NaN (any DK/refused/missing without a Yes) dropped")
    d["BMI"] = (d._BMI5/100).round(2); R("BMI", "_BMI5", "/100; NaN dropped")
    d["Smoking"] = yn("SMOKE100"); R("Smoking", "SMOKE100", "1 Yes, 2 No; 7,9,NaN dropped")
    d["AlcoholDrinking"] = d._RFDRHV7.map({1: "No", 2: "Yes"}); R("AlcoholDrinking", "_RFDRHV7", "heavy drinking: 2->Yes, 1->No; 9 dropped")
    d["Stroke"] = yn("CVDSTRK3"); R("Stroke", "CVDSTRK3", "1 Yes, 2 No; 7,9 dropped")
    d["PhysicalHealth"] = days("PHYSHLTH"); R("PhysicalHealth", "PHYSHLTH", "88->0; 1-30 kept; 77,99 dropped")
    d["MentalHealth"] = days("MENTHLTH"); R("MentalHealth", "MENTHLTH", "88->0; 1-30 kept; 77,99 dropped")
    d["DiffWalking"] = yn("DIFFWALK"); R("DiffWalking", "DIFFWALK", "1 Yes, 2 No; 7,9,NaN dropped")
    d["Sex"] = d.SEXVAR.map({1: "Male", 2: "Female"}); R("Sex", "SEXVAR", "1 Male, 2 Female")
    d["AgeCategory"] = d._AGEG5YR.map(dict(zip(range(1, 14), AGE))); R("AgeCategory", "_AGEG5YR", "1-13 -> 5-year labels; 14 (DK/refused) dropped")
    d["Race"] = d._IMPRACE.map({1: "White", 2: "Black", 3: "Asian", 4: "American Indian/Alaskan Native", 5: "Hispanic", 6: "Other"})
    R("Race", "_IMPRACE", "CDC IMPUTED race/ethnicity: 1 White NH, 2 Black NH, 3 Asian NH, 4 AIAN NH, 5 Hispanic, 6 Other NH (NHPI, other, multiracial); never missing")
    d["Diabetic"] = d.DIABETE4.map({1: "Yes", 2: "Yes (during pregnancy)", 3: "No", 4: "No, borderline diabetes"}); R("Diabetic", "DIABETE4", "1 Yes, 2 Yes (during pregnancy), 3 No, 4 No, borderline; 7,9 dropped")
    d["PhysicalActivity"] = yn("EXERANY2"); R("PhysicalActivity", "EXERANY2", "1 Yes, 2 No; 7,9 dropped")
    d["GenHealth"] = d.GENHLTH.map(GH); R("GenHealth", "GENHLTH", "1-5 labels; 7,9 dropped")
    d["SleepTime"] = d.SLEPTIM1.where(d.SLEPTIM1.between(1, 24)); R("SleepTime", "SLEPTIM1", "1-24 kept; 77,99 dropped")
    d["Asthma"] = yn("ASTHMA3"); R("Asthma", "ASTHMA3", "ever told asthma: 1 Yes, 2 No; 7,9 dropped")
    d["KidneyDisease"] = yn("CHCKDNY2"); R("KidneyDisease", "CHCKDNY2", "1 Yes, 2 No; 7,9 dropped")
    d["SkinCancer"] = yn("CHCSCNCR"); R("SkinCancer", "CHCSCNCR", "1 Yes, 2 No; 7,9 dropped")
    COLS = ["HeartDisease","BMI","Smoking","AlcoholDrinking","Stroke","PhysicalHealth","MentalHealth","DiffWalking","Sex","AgeCategory",
            "Race","Diabetic","PhysicalActivity","GenHealth","SleepTime","Asthma","KidneyDisease","SkinCancer"]
    KF = {"full": "2020/heart_2020_cleaned.csv"}; LABEL = "HeartDisease"; RACE = "Race"; RAWRACE = "_RACE"
else:
    FIPS = {1:"Alabama",2:"Alaska",4:"Arizona",5:"Arkansas",6:"California",8:"Colorado",9:"Connecticut",10:"Delaware",11:"District of Columbia",
            12:"Florida",13:"Georgia",15:"Hawaii",16:"Idaho",17:"Illinois",18:"Indiana",19:"Iowa",20:"Kansas",21:"Kentucky",22:"Louisiana",23:"Maine",
            24:"Maryland",25:"Massachusetts",26:"Michigan",27:"Minnesota",28:"Mississippi",29:"Missouri",30:"Montana",31:"Nebraska",32:"Nevada",
            33:"New Hampshire",34:"New Jersey",35:"New Mexico",36:"New York",37:"North Carolina",38:"North Dakota",39:"Ohio",40:"Oklahoma",41:"Oregon",
            42:"Pennsylvania",44:"Rhode Island",45:"South Carolina",46:"South Dakota",47:"Tennessee",48:"Texas",49:"Utah",50:"Vermont",51:"Virginia",
            53:"Washington",54:"West Virginia",55:"Wisconsin",56:"Wyoming",66:"Guam",72:"Puerto Rico",78:"Virgin Islands"}
    d["State"] = d._STATE.map(FIPS); R("State", "_STATE", "FIPS -> name")
    d["Sex"] = d.SEXVAR.map({1: "Male", 2: "Female"}); R("Sex", "SEXVAR", "1 Male, 2 Female")
    d["GeneralHealth"] = d.GENHLTH.map(GH); R("GeneralHealth", "GENHLTH", "1-5 labels; 7,9 -> NaN")
    d["PhysicalHealthDays"] = days("PHYSHLTH"); d["MentalHealthDays"] = days("MENTHLTH"); R("Physical/MentalHealthDays", "PHYSHLTH/MENTHLTH", "88->0; 77,99 -> NaN")
    d["LastCheckupTime"] = d.CHECKUP1.map({1: "Within past year (anytime less than 12 months ago)", 2: "Within past 2 years (1 year but less than 2 years ago)",
                                           3: "Within past 5 years (2 years but less than 5 years ago)", 4: "5 or more years ago"})
    R("LastCheckupTime", "CHECKUP1", "1-4 labels; 8 (NEVER had a checkup) -> NaN, together with 7,9")
    d["PhysicalActivities"] = yn("EXERANY2"); R("PhysicalActivities", "EXERANY2", "1 Yes, 2 No; 7,9 -> NaN")
    d["SleepHours"] = d.SLEPTIM1.where(d.SLEPTIM1.between(1, 24)); R("SleepHours", "SLEPTIM1", "1-24; 77,99 -> NaN")
    d["RemovedTeeth"] = d.RMVTETH4.map({8: "None of them", 1: "1 to 5", 2: "6 or more, but not all", 3: "All"}); R("RemovedTeeth", "RMVTETH4", "8 None, 1, 2, 3; 7,9 -> NaN")
    for k, s in (("HadHeartAttack","CVDINFR4"),("HadAngina","CVDCRHD4"),("HadStroke","CVDSTRK3"),("HadAsthma","ASTHMA3"),("HadSkinCancer","CHCSCNC1"),
                 ("HadCOPD","CHCCOPD3"),("HadDepressiveDisorder","ADDEPEV3"),("HadKidneyDisease","CHCKDNY2"),("HadArthritis","HAVARTH4"),
                 ("DeafOrHardOfHearing","DEAF"),("BlindOrVisionDifficulty","BLIND"),("DifficultyConcentrating","DECIDE"),("DifficultyWalking","DIFFWALK"),
                 ("DifficultyDressingBathing","DIFFDRES"),("DifficultyErrands","DIFFALON"),("ChestScan","LCSCTSC1"),("AlcoholDrinkers","DRNKANY6"),
                 ("HIVTesting","HIVTST7"),("FluVaxLast12","FLUSHOT7"),("PneumoVaxEver","PNEUVAC4"),("HighRiskLastYear","HIVRISK5")):
        d[k] = yn(s); R(k, s, "1 Yes, 2 No; 7 (don't know), 9 (refused), NaN (not asked) -> NaN")
    d["HadDiabetes"] = d.DIABETE4.map({1: "Yes", 2: "Yes, but only during pregnancy (female)", 3: "No", 4: "No, pre-diabetes or borderline diabetes"}); R("HadDiabetes", "DIABETE4", "4 levels; 7,9 -> NaN")
    d["SmokerStatus"] = d._SMOKER3.map({1: "Current smoker - now smokes every day", 2: "Current smoker - now smokes some days", 3: "Former smoker", 4: "Never smoked"}); R("SmokerStatus", "_SMOKER3", "1-4; 9 -> NaN")
    d["ECigaretteUsage"] = d.ECIGNOW2.map({1: "Never used e-cigarettes in my entire life", 2: "Use them every day", 3: "Use them some days", 4: "Not at all (right now)"}); R("ECigaretteUsage", "ECIGNOW2", "1-4; 7,9 -> NaN")
    d["RaceEthnicityCategory"] = d._RACEGR4.map({1: "White only, Non-Hispanic", 2: "Black only, Non-Hispanic", 3: "Other race only, Non-Hispanic", 4: "Multiracial, Non-Hispanic", 5: "Hispanic"})
    R("RaceEthnicityCategory", "_RACEGR4", "1-5 (NOT imputed); 9 -> NaN; 'Other race only' pools Asian, AIAN, NHPI and other")
    d["AgeCategory"] = d._AGEG5YR.map(dict(zip(range(1, 14), ["Age " + a.replace("-", " to ") if a[0] != "8" else "Age 80 or older" for a in AGE]))); R("AgeCategory", "_AGEG5YR", "1-13; 14 -> NaN")
    d["HeightInMeters"] = (d.HTM4/100).round(2); d["WeightInKilograms"] = (d.WTKG3/100).round(2); d["BMI"] = (d._BMI5/100).round(2); R("Height/Weight/BMI", "HTM4/WTKG3/_BMI5", "/100")
    d["TetanusLast10Tdap"] = d.TETANUS1.map({1: "Yes, received Tdap", 2: "Yes, received tetanus shot, but not Tdap", 3: "Yes, received tetanus shot but not sure what type",
                                             4: "No, did not receive any tetanus shot in the past 10 years"}); R("TetanusLast10Tdap", "TETANUS1", "1-4; 7,9 -> NaN")
    d["CovidPos"] = d.COVIDPOS.map({1: "Yes", 2: "No", 3: "Tested positive using home test without a health professional"}); R("CovidPos", "COVIDPOS", "1-3; 7,9 -> NaN")
    COLS = ["State","Sex","GeneralHealth","PhysicalHealthDays","MentalHealthDays","LastCheckupTime","PhysicalActivities","SleepHours","RemovedTeeth",
            "HadHeartAttack","HadAngina","HadStroke","HadAsthma","HadSkinCancer","HadCOPD","HadDepressiveDisorder","HadKidneyDisease","HadArthritis",
            "HadDiabetes","DeafOrHardOfHearing","BlindOrVisionDifficulty","DifficultyConcentrating","DifficultyWalking","DifficultyDressingBathing",
            "DifficultyErrands","SmokerStatus","ECigaretteUsage","ChestScan","RaceEthnicityCategory","AgeCategory","HeightInMeters","WeightInKilograms",
            "BMI","AlcoholDrinkers","HIVTesting","FluVaxLast12","PneumoVaxEver","TetanusLast10Tdap","HighRiskLastYear","CovidPos"]
    KF = {"with_nans": "2022/heart_2022_with_nans.csv", "no_nans": "2022/heart_2022_no_nans.csv"}; LABEL = "HadHeartAttack"; RACE = "RaceEthnicityCategory"; RAWRACE = "_RACE1"
for r in RULES: print("RULE", r[0], "<-", r[1], ":", r[2])
d["cc"] = d[COLS].notna().all(axis=1)
print("missing after recode per column:", {c: int(d[c].isna().sum()) for c in COLS})
print("complete cases", int(d.cc.sum()), "of", len(d), "share kept", tr(d.cc.mean()))
def key(df):
    out = pd.Series([""]*len(df), index=df.index)
    for c in COLS:
        v = df[c]
        s = v.map(lambda x: "NA" if pd.isna(x) else (f"{x:.2f}" if isinstance(x, float) else str(x)))
        out = out + "|" + s
    return out.value_counts()
def match(a, b, name):
    j = pd.concat([a.rename("a"), b.rename("b")], axis=1).fillna(0)
    m = np.minimum(j.a, j.b).sum()
    print(f"multiset match {name}: rebuild rows {int(j.a.sum())} kaggle rows {int(j.b.sum())} matched {int(m)} rate vs kaggle {tr(m/j.b.sum())}",
          f"| patterns {len(j)} abs row diff {int((j.a-j.b).abs().sum())}")
    return m/j.b.sum()
K = {}
for nm, f in KF.items():
    k = pd.read_csv(kag + "/" + f); K[nm] = k
    print("kaggle", nm, k.shape, "duplicate rows", int(k.duplicated().sum()))
rates = {}
if year == "2020":
    rates["full"] = match(key(d[d.cc]), key(K["full"]), "rebuild complete cases vs heart_2020_cleaned")
    print("rebuild complete cases duplicate rows", int(d[d.cc][COLS].duplicated().sum()))
else:
    rates["with_nans"] = match(key(d), key(K["with_nans"]), "rebuild all respondents vs heart_2022_with_nans")
    rates["no_nans"] = match(key(d[d.cc]), key(K["no_nans"]), "rebuild complete cases vs heart_2022_no_nans")
    print("kaggle with_nans rows with no NaN", int(K["with_nans"].notna().all(axis=1).sum()))
for c in COLS:
    kk = K["full" if year == "2020" else "with_nans"]
    sub = d[d.cc] if year == "2020" else d
    a = sub[c].astype(str).value_counts(); b = kk[c].map(lambda x: "nan" if pd.isna(x) else (f"{x:.2f}" if isinstance(x, float) else str(x))).value_counts()
    a.index = [("nan" if i == "nan" else (f"{float(i):.2f}" if c in ("BMI","PhysicalHealth","MentalHealth","SleepTime","PhysicalHealthDays","MentalHealthDays","SleepHours","HeightInMeters","WeightInKilograms") else i)) for i in a.index]
    a = a.groupby(level=0).sum(); diff = a.sub(b, fill_value=0); diff = diff[diff != 0]
    if len(diff): print(" marginal differs", c, {k2: int(v) for k2, v in list(diff.items())[:8]})
# ---------- audit ----------
def wprev(df, y):
    w = df._LLCPWT.values; yy = df[y].values.astype(float); p = (w*yy).sum()/w.sum()
    z = pd.DataFrame({"h": df._STSTR.values, "psu": df._PSU.values, "z": w*(yy-p)/w.sum()})
    t = z.groupby(["h","psu"]).z.sum().reset_index(); v = 0.0
    for h, g in t.groupby("h"):
        n = len(g)
        if n >= 2: v += n/(n-1)*((g.z-g.z.mean())**2).sum()
    return p, math.sqrt(v)
def h(p1, p2): return abs(2*math.asin(math.sqrt(p1))-2*math.asin(math.sqrt(p2)))
def kish(w): return w.sum()**2/(w**2).sum()
print("\n== LABEL ==")
ct = pd.crosstab(d.CVDINFR4.fillna(-1).astype(int), d.CVDCRHD4.fillna(-1).astype(int), margins=True); print("CVDINFR4 (rows, MI) x CVDCRHD4 (cols, CHD/angina), all respondents\n", ct)
mdk = ((d.CVDINFR4.isin([7, 9]) | d.CVDINFR4.isna()) & (d.CVDCRHD4 == 2)) | ((d.CVDCRHD4.isin([7, 9]) | d.CVDCRHD4.isna()) & (d.CVDINFR4 == 2))
print("_MICHD NaN", int(d._MICHD.isna().sum()), "of which one item No and the other DK/refused/missing", int((d._MICHD.isna() & mdk).sum()))
d["michd"] = (d._MICHD == 1).astype(float).where(d._MICHD.notna())
d["mi"] = (d.CVDINFR4 == 1).astype(float).where(d.CVDINFR4.isin([1, 2]))
d["chd_only"] = ((d.CVDCRHD4 == 1) & (d.CVDINFR4 == 2)).astype(float)
pop = d[d._MICHD.notna()]
fileset = d[d.cc]
print("label composition among _MICHD=1 (all respondents): MI only", int(((d.CVDINFR4 == 1) & (d.CVDCRHD4 != 1)).sum()),
      "CHD/angina only", int(((d.CVDCRHD4 == 1) & (d.CVDINFR4 != 1)).sum()), "both", int(((d.CVDINFR4 == 1) & (d.CVDCRHD4 == 1)).sum()))
if year == "2022":
    f = fileset
    ha = pd.crosstab(f.HadHeartAttack, f.HadAngina); print("no_nans file HadHeartAttack x HadAngina\n", ha)
    print(" P(HadAngina=Yes | HadHeartAttack=Yes)", tr((f[f.HadHeartAttack == "Yes"].HadAngina == "Yes").mean()),
          " P(HadAngina=Yes | HadHeartAttack=No)", tr((f[f.HadHeartAttack == "No"].HadAngina == "Yes").mean()))
    print(" no_nans rows with CHD/angina but HadHeartAttack=No (would be HeartDisease=Yes under the 2020 definition)", int(((f.HadAngina == "Yes") & (f.HadHeartAttack == "No")).sum()),
          "| 2020-style _MICHD=Yes rows in no_nans", int((f._MICHD == 1).sum()), "| HadHeartAttack=Yes", int((f.HadHeartAttack == "Yes").sum()))
    for nm, df in (("all respondents, valid CVDINFR4", d[d.mi.notna()]), ("no_nans file", f)):
        p, se = wprev(df, "mi"); print(f" HadHeartAttack prevalence {nm} n={len(df)}: unweighted {tr(df.mi.mean())} weighted {tr(p)} SE {tr(se)}")
for nm, df in (("all valid _MICHD respondents", pop), ("file population (complete cases)", fileset)):
    p, se = wprev(df, "michd"); print(f"CHD-or-MI (_MICHD) prevalence {nm} n={len(df)}: unweighted {tr(df.michd.mean())} weighted {tr(p)} design SE {tr(se)}")
print("\n== RACE ==")
print("raw race in file population (", RAWRACE, ") x file race:\n", pd.crosstab(fileset[RAWRACE].fillna(-1).astype(int), fileset[RACE].fillna("NaN")))
if year == "2020":
    print("file rows whose race is CDC-imputed (_RACE = 9 DK/refused or missing)", int((fileset._RACE.isna() | (fileset._RACE == 9)).sum()), "of", len(fileset))
    print("file 'Other' rows by _RACE: NHPI(5)", int(((fileset.Race == "Other") & (fileset._RACE == 5)).sum()), "other(6)", int(((fileset.Race == "Other") & (fileset._RACE == 6)).sum()),
          "multiracial(7)", int(((fileset.Race == "Other") & (fileset._RACE == 7)).sum()), "DK/refused imputed(9)", int(((fileset.Race == "Other") & (fileset._RACE == 9)).sum()))
    imp = fileset[(fileset._RACE == 9) | fileset._RACE.isna()]
    print(" imputed-race rows by assigned Race", imp.Race.value_counts().to_dict(), "| CHD-or-MI unweighted in imputed rows", tr(imp.michd.mean()), "vs non-imputed", tr(fileset[~fileset.index.isin(imp.index)].michd.mean()))
print("\n== ROW LOSS BY GROUP (complete-case drop) ==")
base = d.copy()
base["ageg"] = base._AGEG5YR.where(base._AGEG5YR.between(1, 13)); base["race"] = base[RAWRACE if year == "2022" else "_IMPRACE"]
for g, lab in (("race", "race (" + ("_RACE1" if year == "2022" else "_IMPRACE") + ")"), ("ageg", "age group _AGEG5YR"), ("SEXVAR", "sex")):
    rows = []
    for k2, s in base.groupby(g):
        w = s._LLCPWT
        rows.append((int(k2), len(s), int(s.cc.sum()), s.cc.mean(), np.average(s.cc, weights=w),
                     s[s._MICHD.notna()].michd.mean(), (np.average(s[s._MICHD.notna()].michd, weights=s[s._MICHD.notna()]._LLCPWT) if s._MICHD.notna().any() else float("nan")),
                     s[s.cc].michd.mean() if s.cc.any() else float("nan"), np.average(s[s.cc].michd, weights=s[s.cc]._LLCPWT) if s.cc.any() else float("nan")))
    t = pd.DataFrame(rows, columns=[g, "n_raw", "n_file", "kept_unw", "kept_w", "chdmi_all_unw", "chdmi_all_w", "chdmi_file_unw", "chdmi_file_w"])
    print(lab); print(t.to_string(index=False, float_format=lambda x: f"{tr(x):.4f}"))
    print(f"  Cohen h of retained share (max-min): unweighted {tr(h(t.kept_unw.max(), t.kept_unw.min()))} weighted {tr(h(t.kept_w.max(), t.kept_w.min()))}")
    t["shift_w"] = t.chdmi_file_w - t.chdmi_all_w
    print(f"  max within-group Cohen h, CHD-or-MI weighted all vs file", tr(max(h(a, b) for a, b in zip(t.chdmi_all_w, t.chdmi_file_w))))
    # composition shift: group share of weighted population vs of file
    sh_all = base.groupby(g)._LLCPWT.sum()/base._LLCPWT.sum(); sh_file = base[base.cc].groupby(g)._LLCPWT.sum()/base[base.cc]._LLCPWT.sum()
    sh_unw = base[base.cc].groupby(g).size()/base.cc.sum()
    print("  group share: weighted population", {int(k): tr(v) for k, v in sh_all.items()}, "| unweighted file", {int(k): tr(v) for k, v in sh_unw.items()},
          "| max Cohen h (pop weighted vs file unweighted)", tr(max(h(sh_all[k], sh_unw.get(k, 0)) for k in sh_all.index)))
print("\n== WHICH COLUMNS DRIVE THE DROP ==")
miss = d[COLS].isna(); only = miss[miss.sum(axis=1) == 1]
print("rows dropped", int((~d.cc).sum()), "| dropped because of exactly one column:", {c: int(v) for c, v in only.sum().sort_values(ascending=False).items() if v > 0})
if year == "2022":
    dk = {"PneumoVaxEver": d.PNEUVAC4 == 7, "TetanusLast10Tdap": d.TETANUS1 == 7, "ChestScan": d.LCSCTSC1 == 7, "HIVTesting": d.HIVTST7 == 7,
          "LastCheckupTime(never)": d.CHECKUP1 == 8, "CovidPos": d.COVIDPOS == 7}
    for k2, m in dk.items(): print(f" {k2}: 'don't know'/'never' answers coded NaN {int(m.sum())}")
    anydk = pd.concat(dk.values(), axis=1).any(axis=1)
    print(" rows with at least one such answer", int(anydk.sum()), "| all of them excluded from no_nans:", int((anydk & d.cc).sum()) == 0)
    nh = ["PneumoVaxEver","TetanusLast10Tdap","HIVTesting","FluVaxLast12","HighRiskLastYear","CovidPos","ChestScan","ECigaretteUsage","AlcoholDrinkers","LastCheckupTime"]
    cc_core = d[[c for c in COLS if c not in nh]].notna().all(axis=1)
    print(" complete cases if only the 30 health/demographic columns were required:", int(cc_core.sum()), "| lost only because of the 10 vaccine/test/behaviour columns", int((cc_core & ~d.cc).sum()))
    ck = d[d.CHECKUP1 == 8]; print(" never-checkup respondents: n", len(ck), "MI unweighted", tr(ck.mi.mean()), "age>=65 share", tr((ck._AGEG5YR.between(10, 13)).mean()), "vs all", tr(d._AGEG5YR.between(10, 13).mean()))
d.to_pickle(outp)
print("saved", outp, "| P1 rebuild:", {k: ("PASS" if v >= 0.99 else "FAIL") + f" {tr(v)}" for k, v in rates.items()})
