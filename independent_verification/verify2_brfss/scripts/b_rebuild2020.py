"""B + D. Independent rebuild of Kaggle heart_2020_cleaned from raw LLCP2020; MI share; race imputation."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import pandas as pd, numpy as np
V = WORK_ROOT + '/verify2'
kag = pd.read_csv(f'{V}/kaggle/heart_2020_cleaned.csv')
raw = pd.read_parquet(f'{V}/raw/raw2020.parquet')
out = open(f'{V}/b_out.txt', 'w', encoding='utf-8')
def P(*a):
    print(*a); print(*a, file=out, flush=True)
def tr(x): return int(x * 10000) / 10000

P('Kaggle 2020 rows', len(kag))
for c in kag.columns:
    v = kag[c].value_counts()
    P(' ', c, len(v), dict(v.head(8)) if len(v) < 20 else f'min {kag[c].min()} max {kag[c].max()}')
P('raw rows', len(raw))
for c in raw.columns:
    if c == 'SEQNO': continue
    P(' raw', c, 'NaN', int(raw[c].isna().sum()), dict(raw[c].value_counts().head(10)) if raw[c].nunique() < 30 else f'min {raw[c].min()} max {raw[c].max()}')

yn = {1: 'Yes', 2: 'No'}
age = {1: '18-24', 2: '25-29', 3: '30-34', 4: '35-39', 5: '40-44', 6: '45-49', 7: '50-54', 8: '55-59', 9: '60-64',
       10: '65-69', 11: '70-74', 12: '75-79', 13: '80 or older'}
race = {1: 'White', 2: 'Black', 3: 'Asian', 4: 'American Indian/Alaskan Native', 5: 'Hispanic', 6: 'Other'}
gh = {1: 'Excellent', 2: 'Very good', 3: 'Good', 4: 'Fair', 5: 'Poor'}
dia = {1: 'Yes', 2: 'Yes (during pregnancy)', 3: 'No', 4: 'No, borderline diabetes'}

r = raw.copy()
d = pd.DataFrame(index=r.index)
d['HeartDisease'] = r._MICHD.map(yn)
d['BMI'] = r._BMI5 / 100
d['Smoking'] = r.SMOKE100.map(yn)
d['AlcoholDrinking'] = r._RFDRHV7.map({1: 'No', 2: 'Yes'})
d['Stroke'] = r.CVDSTRK3.map(yn)
d['PhysicalHealth'] = r.PHYSHLTH.replace({88: 0}).where(r.PHYSHLTH.between(0, 30) | (r.PHYSHLTH == 88))
d['MentalHealth'] = r.MENTHLTH.replace({88: 0}).where(r.MENTHLTH.between(0, 30) | (r.MENTHLTH == 88))
d['DiffWalking'] = r.DIFFWALK.map(yn)
d['Sex'] = r.SEXVAR.map({1: 'Male', 2: 'Female'})
d['AgeCategory'] = r._AGEG5YR.map(age)
d['Race'] = r._IMPRACE.map(race)
d['Diabetic'] = r.DIABETE4.map(dia)
d['PhysicalActivity'] = r.EXERANY2.map(yn)
d['GenHealth'] = r.GENHLTH.map(gh)
d['SleepTime'] = r.SLEPTIM1.where(r.SLEPTIM1.between(1, 24))
d['Asthma'] = r.ASTHMA3.map(yn)
d['KidneyDisease'] = r.CHCKDNY2.map(yn)
d['SkinCancer'] = r.CHCSCNCR.map(yn)
keep = d.notna().all(axis=1)
reb = d[keep]
P('\nrebuilt rows', len(reb), 'vs Kaggle', len(kag))

def norm(df):
    x = df.copy()
    for c in ['BMI', 'PhysicalHealth', 'MentalHealth', 'SleepTime']:
        x[c] = x[c].astype(float).round(4)
    return x
ca = norm(reb).value_counts(); cb = norm(kag).value_counts()
j = pd.concat([ca.rename('a'), cb.rename('b')], axis=1).fillna(0)
P('multiset match', np.minimum(j.a, j.b).sum() / max(len(reb), len(kag)), 'tuples differing', int((j.a != j.b).sum()))
for c in kag.columns:
    if not norm(reb)[c].value_counts().sort_index().equals(norm(kag)[c].value_counts().sort_index()):
        P(' marginal differs', c)

rr = raw.loc[reb.index]
hd = reb.HeartDisease == 'Yes'
P('\nB. HeartDisease == _MICHD by construction; Kaggle HeartDisease Yes', int((kag.HeartDisease == 'Yes').sum()), 'rebuild Yes', int(hd.sum()))
P(' rebuild HD=Yes CVDINFR4 value counts', dict(rr.loc[hd, 'CVDINFR4'].value_counts(dropna=False)))
noMI = int((rr.loc[hd, 'CVDINFR4'] != 1).sum())
P(' HD=Yes with CVDINFR4 != 1:', noMI, '/', int(hd.sum()), '=', tr(noMI / hd.sum()))
P(' HD=Yes with CVDINFR4 == 2 (explicit no MI):', int((rr.loc[hd, 'CVDINFR4'] == 2).sum()))
P(' _MICHD definition check (raw): _MICHD==1 iff CVDINFR4==1 or CVDCRHD4==1:',
  pd.crosstab(raw._MICHD.fillna(-1), (raw.CVDINFR4 == 1) | (raw.CVDCRHD4 == 1)).to_dict())
rawhd = raw._MICHD == 1
P(' raw level: _MICHD==1', int(rawhd.sum()), 'CVDINFR4!=1 among them', int((raw.loc[rawhd, 'CVDINFR4'] != 1).sum()))

P('\nD. 2020 race')
P(' rebuild _RACE value counts', dict(rr._RACE.value_counts(dropna=False)))
r9 = rr._RACE == 9
P(' rebuild rows with _RACE==9:', int(r9.sum()), 'imputed race counts', dict(reb.loc[r9, 'Race'].value_counts()))
P(' raw rows _RACE==9:', int((raw._RACE == 9).sum()), '; raw _IMPRACE among them', dict(raw.loc[raw._RACE == 9, '_IMPRACE'].value_counts()))
out.close()
