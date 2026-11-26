import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nhfs_parse as P, csv, collections
P.lower_priority()
lay, recs = P.read()
print(len(lay), len(recs))
print(collections.Counter(r["SUBGROUP"] for r in recs))
print(collections.Counter(len(l.rstrip("\r\n")) for l in open(P.RAW+"nhfspuf.dat",encoding="latin-1")).most_common(5))
print([r["FLUWT"] for r in recs[:3]], open(P.RAW+"nhfspuf.dat",encoding="latin-1").readline()[216:237])
ad=[r for r in recs if r["SUBGROUP"]=="A"]
for v in ["N_ADULT_R","HH_CHILD_R","AGEGRP","INC_POV","RACEETH4_I","RACE_I_R","MSA3_I","INSURE","C_INSURE2","Q95","VACC_H1N1_F","VACC_SEAS_F","HQ23","HQ24","HQ24_B","Q23","Q24","Q24_B","EDUCATION_COMP","RENT_OWN_R","MARITAL","SEX_I","HHS_REGION","Q95_INDSTR","Q95_OCCPN"]:
    print(v, sorted(collections.Counter(r[v] for r in ad).items(), key=lambda x:str(x[0])))
pub = list(csv.DictReader(open(SURVEY_DATA_ROOT + "/flushot-kaggle/raw/training_set_features.csv")))+list(csv.DictReader(open(SURVEY_DATA_ROOT + "/flushot-kaggle/raw/test_set_features.csv")))
print(len(pub))
for c in pub[0]:
    if c=="respondent_id": continue
    cnt=collections.Counter(p[c] for p in pub)
    print(c, len(cnt), sorted(cnt.items())[:15])
