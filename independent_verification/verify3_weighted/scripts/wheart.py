"""verify3 heart: weighted prevalences + Taylor SE (2020, 2022), duplicates, 2020 race pooling, 21,616 / 8,181."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np
from svy import report, tr4
V3 = WORK_ROOT + '/verify3'
R = V3 + '/raw'
out = open(f'{V3}/wheart_out.txt', 'w', encoding='utf-8')
def P(*a):
    print(*a); print(*a, file=out, flush=True)

# ---------------- 2020 ----------------
kag = pd.read_csv(f'{R}/heart_2020_cleaned.csv')
raw = pd.read_parquet(f'{R}/raw2020.parquet')
P('2020 raw rows', len(raw), '; Kaggle rows', len(kag))
yn = {1: 'Yes', 2: 'No'}
age = {1: '18-24', 2: '25-29', 3: '30-34', 4: '35-39', 5: '40-44', 6: '45-49', 7: '50-54', 8: '55-59', 9: '60-64',
       10: '65-69', 11: '70-74', 12: '75-79', 13: '80 or older'}
race = {1: 'White', 2: 'Black', 3: 'Asian', 4: 'American Indian/Alaskan Native', 5: 'Hispanic', 6: 'Other'}
r = raw
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
d['Diabetic'] = r.DIABETE4.map({1: 'Yes', 2: 'Yes (during pregnancy)', 3: 'No', 4: 'No, borderline diabetes'})
d['PhysicalActivity'] = r.EXERANY2.map(yn)
d['GenHealth'] = r.GENHLTH.map({1: 'Excellent', 2: 'Very good', 3: 'Good', 4: 'Fair', 5: 'Poor'})
d['SleepTime'] = r.SLEPTIM1.where(r.SLEPTIM1.between(1, 24))
d['Asthma'] = r.ASTHMA3.map(yn)
d['KidneyDisease'] = r.CHCKDNY2.map(yn)
d['SkinCancer'] = r.CHCSCNCR.map(yn)
reb = d[d.notna().all(axis=1)]
def norm(x):
    x = x.copy()
    for c in ['BMI', 'PhysicalHealth', 'MentalHealth', 'SleepTime']:
        x[c] = x[c].astype(float).round(4)
    return x
ca, cb = norm(reb).value_counts(), norm(kag).value_counts()
j = pd.concat([ca.rename('a'), cb.rename('b')], axis=1).fillna(0)
P('rebuild rows', len(reb), 'multiset match', np.minimum(j.a, j.b).sum() / len(kag), 'differing tuples', int((j.a != j.b).sum()))
nd = int(kag.duplicated().sum())
P('Kaggle 2020 exact duplicate rows beyond first', nd, 'share', tr4(nd / len(kag)), '; rebuild duplicates', int(norm(reb).duplicated().sum()))
hd = (kag.HeartDisease == 'Yes')
P('unweighted HeartDisease=Yes', int(hd.sum()), '/', len(kag), '=', tr4(hd.mean()))
valid = raw._MICHD.isin([1, 2]).values
fp = np.zeros(len(raw), bool); fp[reb.index] = True
y = (raw._MICHD == 1).astype(float).values
P('_MICHD codes', dict(raw._MICHD.value_counts(dropna=False)), '; valid', int(valid.sum()))
report(P, '2020 _MICHD, all valid respondents', y, raw._LLCPWT.values, raw._STSTR.values, raw._PSU.values, valid)
report(P, '2020 _MICHD, file population', y, raw._LLCPWT.values, raw._STSTR.values, raw._PSU.values, fp)

rr = raw.loc[reb.index]
oth = reb.Race == 'Other'
P('\n2020 Race=Other rows: rebuild', int(oth.sum()), '; Kaggle', int((kag.Race == 'Other').sum()))
P(' _RACE among rebuild Other (5 NHPI, 6 other race only, 7 multiracial, 9 DK/refused):', dict(rr.loc[oth, '_RACE'].value_counts(dropna=False).sort_index()))
P(' _IMPRACE vs _RACE crosstab in file rows:\n', pd.crosstab(rr._RACE, rr._IMPRACE).to_string())
del raw, reb, d, rr, kag

# ---------------- 2022 ----------------
wn = pd.read_csv(f'{R}/heart_2022_with_nans.csv')
nn = pd.read_csv(f'{R}/heart_2022_no_nans.csv')
raw = pd.read_parquet(f'{R}/raw2022.parquet')
P('\n2022 raw rows', len(raw), 'with_nans', len(wn), 'no_nans', len(nn))
P('alignment: crosstab raw CVDINFR4 vs with_nans HadHeartAttack\n', pd.crosstab(raw.CVDINFR4.fillna(-1), wn.HadHeartAttack.fillna('NaN')).to_string())
P('alignment: crosstab raw CVDCRHD4 vs with_nans HadAngina\n', pd.crosstab(raw.CVDCRHD4.fillna(-1), wn.HadAngina.fillna('NaN')).to_string())
for name, f in [('with_nans', wn), ('no_nans', nn)]:
    ndup = int(f.duplicated().sum())
    P(f'{name}: exact duplicate rows beyond first {ndup} (NaN treated as equal), share {tr4(ndup / len(f))}')
ndup_nonan = int(wn[wn.notna().all(axis=1)].duplicated().sum())
P('with_nans complete rows duplicates', ndup_nonan)
ha = nn.HadHeartAttack == 'Yes'; an = nn.HadAngina == 'Yes'
P('\nno_nans: HadHeartAttack Yes', int(ha.sum()), '; No', int((~ha).sum()), '; unweighted rate', tr4(ha.mean()))
P(' HadAngina Yes | HA Yes', int((an & ha).sum()), '; HadAngina Yes | HA No', int((an & ~ha).sum()))
u = int((ha | an).sum())
P(' 2020-style positives (HA or angina):', u, '; of which HA No', int((an & ~ha).sum()), '; share', (an & ~ha).sum() / u, 'trunc', tr4((an & ~ha).sum() / u))
cc = wn.notna().all(axis=1).values
P(' complete cases of with_nans', int(cc.sum()), '; raw _MICHD==1 among them', int((raw._MICHD[cc] == 1).sum()),
  '; raw CVDINFR4==1 or CVDCRHD4==1 among them', int(((raw.CVDINFR4 == 1) | (raw.CVDCRHD4 == 1))[cc].sum()))
validmi = raw.CVDINFR4.isin([1, 2]).values
y = (raw.CVDINFR4 == 1).astype(float).values
P('CVDINFR4 codes', dict(raw.CVDINFR4.value_counts(dropna=False)), '; valid', int(validmi.sum()))
report(P, '2022 CVDINFR4=1, all valid respondents', y, raw._LLCPWT.values, raw._STSTR.values, raw._PSU.values, validmi)
report(P, '2022 CVDINFR4=1, complete-case population', y, raw._LLCPWT.values, raw._STSTR.values, raw._PSU.values, cc)

P('\nArithmetic: 445132-246022 =', 445132 - 246022, '; 98073/199110 =', 98073 / 199110, 'trunc', tr4(98073 / 199110))
P(' 18078/319795 trunc', tr4(18078 / 319795), '; 401958-319795 =', 401958 - 319795)
out.close()
