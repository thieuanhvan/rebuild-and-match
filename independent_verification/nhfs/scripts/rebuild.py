"""Rebuild DrivenData Flu Shot Learning rows from NHFS PUF adults and compare as multisets."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import sys, csv, collections, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nhfs_parse as P
P.lower_priority()
OUT = WORK_ROOT + "/verify_nhfs_independent/"
PUB = SURVEY_DATA_ROOT + "/flushot-kaggle/raw/"
NA = "<NA>"


def T(x):  # truncate (never round) to 4 decimals
    return f"{math.floor(x * 10000) / 10000:.4f}"


def flag(v):  # FLAG format 0/1, '.' missing
    return NA if v is None else str(v)


def concern(r):
    for k, val in (("CONCERN_NONE_F", "0"), ("CONCERN_NOTV_F", "1"), ("CONCERN_SOME_F", "2"), ("CONCERN_VERY_F", "3")):
        if r[k] == 1:
            return val
    return NA  # DKNW / REFD / missing


def knowledge(r):
    for k, val in (("KNOW_H1N1_NONE_F", "0"), ("KNOW_H1N1_LITL_F", "1"), ("KNOW_H1N1_ALOT_F", "2")):
        if r[k] == 1:
            return val
    return NA


def docrec(r, which):
    if r["DOCREC_BOTH_F"] is None:
        return NA
    if r["DOCREC_DKNW_F"] == 1 or r["DOCREC_REFD_F"] == 1:
        return NA
    return "1" if (r["DOCREC_BOTH_F"] == 1 or r[which] == 1) else "0"


# INFERRED from published distributions (codebook has only 01-04/77/99 codes, no 1-5 scale):
OP = {"04": "1", "03": "2", "77": "3", "02": "4", "01": "5"}
AGE = {3: "18 - 34 Years", 4: "35 - 44 Years", 5: "45 - 54 Years", 6: "55 - 64 Years", 7: "65+ Years"}
EDU = {1: "< 12 Years", 2: "12 Years", 3: "Some College", 4: "College Graduate"}
RACE = {1: "Hispanic", 2: "Black", 3: "White", 4: "Other or Multiple"}
SEX = {1: "Male", 2: "Female"}
POV = {1: "> $75,000", 2: "<= $75,000, Above Poverty", 3: "Below Poverty"}  # 4 Unknown -> NA
MAR = {1: "Married", 2: "Not Married"}
RENT = {"01": "Own", "02": "Rent"}
EMP = {"01": "Employed", "02": "Unemployed", "03": "Not in Labor Force"}
MSA = {1: "MSA, Principle City", 2: "MSA, Not Principle  City", 3: "Non-MSA"}
INS = {"01": "1", "02": "0"}


def g(d, v):
    return d.get(v, NA)


FEATS = ["h1n1_concern", "h1n1_knowledge", "behavioral_antiviral_meds", "behavioral_avoidance", "behavioral_face_mask",
         "behavioral_wash_hands", "behavioral_large_gatherings", "behavioral_outside_home", "behavioral_touch_face",
         "doctor_recc_h1n1", "doctor_recc_seasonal", "chronic_med_condition", "child_under_6_months", "health_worker",
         "health_insurance", "opinion_h1n1_vacc_effective", "opinion_h1n1_risk", "opinion_h1n1_sick_from_vacc",
         "opinion_seas_vacc_effective", "opinion_seas_risk", "opinion_seas_sick_from_vacc", "age_group", "education",
         "race", "sex", "income_poverty", "marital_status", "rent_or_own", "employment_status", "census_msa",
         "household_adults", "household_children"]


def rebuild(r):
    return (concern(r), knowledge(r), flag(r["B_H1N1_ANTIV"]), flag(r["B_H1N1_AVOID"]), flag(r["B_H1N1_FMASK"]),
            flag(r["B_H1N1_HANDS"]), flag(r["B_H1N1_LARGE"]), flag(r["B_H1N1_RCONT"]), flag(r["B_H1N1_TOUCH"]),
            docrec(r, "DOCREC_H1N1_F"), docrec(r, "DOCREC_SEAS_F"), flag(r["CHRONIC_MED_F"]),
            flag(r["CLOSE_UNDER6MO_F"]), flag(r["HEALTH_WORKER_F"]), g(INS, r["INSURE"]),
            g(OP, r["HQ23"]), g(OP, r["HQ24"]), g(OP, r["HQ24_B"]), g(OP, r["Q23"]), g(OP, r["Q24"]), g(OP, r["Q24_B"]),
            g(AGE, r["AGEGRP"]), g(EDU, r["EDUCATION_COMP"]), g(RACE, r["RACEETH4_I"]), g(SEX, r["SEX_I"]),
            g(POV, r["INC_POV"]), g(MAR, r["MARITAL"]), g(RENT, r["RENT_OWN_R"]), g(EMP, r["Q95"]),
            g(MSA, r["MSA3_I"]),
            NA if r["N_ADULT_R"] is None else str(r["N_ADULT_R"] - 1),  # INFERRED: published = N_ADULT_R - 1
            NA if r["HH_CHILD_R"] is None else str(r["HH_CHILD_R"]))


def labels(r):
    return (flag(r["VACC_H1N1_F"]), flag(r["VACC_SEAS_F"]))


def load_pub():
    def rd(fn):
        return list(csv.DictReader(open(PUB + fn, encoding="utf-8")))
    tr, te, lab = rd("training_set_features.csv"), rd("test_set_features.csv"), rd("training_set_labels.csv")
    labd = {x["respondent_id"]: (x["h1n1_vaccine"], x["seasonal_vaccine"]) for x in lab}

    def key(p):
        return tuple(p[c] if p[c] != "" else NA for c in FEATS)
    return tr, te, labd, key


def main():
    lay, recs = P.read()
    adults = [r for r in recs if r["SUBGROUP"] == "A"]
    tr, te, labd, key = load_pub()
    lines = []
    w = lines.append
    w(f"Task 1: raw records = {len(recs)}; SUBGROUP (col 20) A = {len(adults)} adults, "
      f"C = {sum(r['SUBGROUP'] == 'C' for r in recs)} children")

    A = collections.Counter(rebuild(r) for r in adults)
    pubk = [key(p) for p in tr] + [key(p) for p in te]
    Pc = collections.Counter(pubk)
    matched = sum(min(Pc[k], A[k]) for k in Pc)
    n = len(pubk)
    w(f"Task 3: published rows (train {len(tr)} + test {len(te)}) = {n}; matched (min-count multiset, "
      f"{len(FEATS)} columns) = {matched}; rate = {T(matched / n)}")
    AL = collections.Counter(rebuild(r) + labels(r) for r in adults)
    TL = collections.Counter(key(p) + labd[p["respondent_id"]] for p in tr)
    mtl = sum(min(TL[k], AL[k]) for k in TL)
    w(f"Task 3b: training rows with 2 labels appended = {len(tr)}; matched = {mtl}; rate = {T(mtl / len(tr))}")

    # Task 4. Within a feature key k, absent = max(0, A[k] - Pc[k]).
    bykey = collections.defaultdict(lambda: [0, 0])  # [both labels valid, >=1 label missing]
    for r in adults:
        bykey[rebuild(r)][0 if NA not in labels(r) else 1] += 1
    abs_tot = miss_pref = miss_lo = miss_hi = 0
    for k, (v, m) in bykey.items():
        c = min(Pc.get(k, 0), v + m)
        a = v + m - c
        abs_tot += a
        miss_pref += m - max(0, c - v)   # published rows consume valid-label adults first
        miss_lo += max(0, m - c)
        miss_hi += min(m, a)
    nmiss = sum(m for v, m in bykey.values())
    w(f"Task 4: adults = {len(adults)}; adults not consumed = {abs_tot}; adults with >=1 missing label (raw) = {nmiss}")
    w(f"  rule: in each feature-tuple group, published rows consume adults with both labels valid first")
    w(f"  absent with >=1 missing label = {miss_pref}; absent with both labels present = {abs_tot - miss_pref}")
    w(f"  bounds over any within-group assignment: missing-label absent in [{miss_lo}, {miss_hi}]")
    w(f"  published rows not matched to any adult = {n - matched}")

    h = [int(labd[p['respondent_id']][0]) for p in tr]
    s = [int(labd[p['respondent_id']][1]) for p in tr]
    w(f"Task 5: published training unweighted means: h1n1_vaccine = {T(sum(h) / len(h))}, "
      f"seasonal_vaccine = {T(sum(s) / len(s))}")
    for nm, var in (("H1N1", "VACC_H1N1_F"), ("seasonal", "VACC_SEAS_F")):
        vv = [r for r in adults if r[var] is not None]
        ww = sum(r["FLUWT"] for r in vv)
        yy = sum(r["FLUWT"] for r in vv if r[var] == 1)
        w(f"  FLUWT-weighted {nm} prevalence, adults with valid {var} (n={len(vv)}) = {T(yy / ww)}; "
          f"unweighted = {T(sum(r[var] for r in vv) / len(vv))}")
    open(OUT + "rebuild_out.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return adults, A, Pc


if __name__ == "__main__":
    main()
