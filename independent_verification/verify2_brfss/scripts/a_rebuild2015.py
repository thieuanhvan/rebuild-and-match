"""A. Independent rebuild of the Kaggle 21-feature BRFSS 2015 diabetes_012 file from raw LLCP2015."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import pandas as pd, numpy as np
V = WORK_ROOT + '/verify2'
K = SURVEY_DATA_ROOT + '/kaggle-diabetes-2015/diabetes_012_health_indicators_BRFSS2015.csv'
kag = pd.read_csv(K)
out = open(f'{V}/a_out.txt', 'w', encoding='utf-8')
def P(*a):
    print(*a); print(*a, file=out, flush=True)

P('Kaggle 012 rows', len(kag))
for c in kag.columns:
    v = sorted(kag[c].unique())
    P(' ', c, len(v), v[:12], '...' if len(v) > 12 else '')

raw = pd.read_parquet(f'{V}/raw/raw2015.parquet')
P('raw 2015 rows', len(raw))
feat = ['DIABETE3', '_RFHYPE5', 'TOLDHI2', '_CHOLCHK', '_BMI5', 'SMOKE100', 'CVDSTRK3', '_MICHD', '_TOTINDA',
        '_FRTLT1', '_VEGLT1', '_RFDRHV5', 'HLTHPLN1', 'MEDCOST', 'GENHLTH', 'MENTHLTH', 'PHYSHLTH', 'DIFFWALK',
        'SEX', '_AGEG5YR', 'EDUCA', 'INCOME2']
for c in feat:
    vc = raw[c].value_counts(dropna=False)
    P(' raw', c, 'n_unique', raw[c].nunique(dropna=False), 'NaN', int(raw[c].isna().sum()),
      dict(vc.head(12)) if raw[c].nunique() < 40 else f'min {raw[c].min()} max {raw[c].max()}')

def build(df, bmi_mode):
    d = df[feat].dropna().copy()
    d = d[~d.DIABETE3.isin([7, 9])]
    orig_dia = d.DIABETE3.copy()
    d['DIABETE3'] = d.DIABETE3.map({1: 2, 2: 0, 3: 0, 4: 1})
    d = d[d._RFHYPE5 != 9]; d['_RFHYPE5'] = d._RFHYPE5.map({1: 0, 2: 1})
    d = d[~d.TOLDHI2.isin([7, 9])]; d['TOLDHI2'] = d.TOLDHI2.map({1: 1, 2: 0})
    d = d[d._CHOLCHK != 9]; d['_CHOLCHK'] = d._CHOLCHK.map({1: 1, 2: 0, 3: 0})
    b = d._BMI5 / 100
    d['_BMI5'] = b.round(0) if bmi_mode == 'pandas_round' else np.floor(b + 0.5)
    for c in ['SMOKE100', 'CVDSTRK3', 'HLTHPLN1', 'MEDCOST', 'DIFFWALK']:
        d = d[~d[c].isin([7, 9])]; d[c] = d[c].map({1: 1, 2: 0})
    d['_MICHD'] = d._MICHD.map({1: 1, 2: 0})
    for c in ['_TOTINDA', '_FRTLT1', '_VEGLT1']:
        d = d[d[c] != 9]; d[c] = d[c].map({1: 1, 2: 0})
    d = d[d._RFDRHV5 != 9]; d['_RFDRHV5'] = d._RFDRHV5.map({1: 0, 2: 1})
    d = d[~d.GENHLTH.isin([7, 9])]
    for c in ['MENTHLTH', 'PHYSHLTH']:
        d = d[~d[c].isin([77, 99])]; d[c] = d[c].replace({88: 0})
    d['SEX'] = d.SEX.map({1: 1, 2: 0})
    d = d[d._AGEG5YR != 14]
    d = d[d.EDUCA != 9]
    d = d[~d.INCOME2.isin([77, 99])]
    d.columns = list(kag.columns)
    return d.astype(float), orig_dia.loc[d.index]

def multiset_match(a, b):
    ca = a.value_counts(); cb = b.value_counts()
    j = pd.concat([ca.rename('a'), cb.rename('b')], axis=1).fillna(0)
    inter = np.minimum(j.a, j.b).sum()
    return inter / max(len(a), len(b)), int((j.a != j.b).sum())

for mode in ['pandas_round', 'half_up']:
    d, dia = build(raw, mode)
    m, ndiff = multiset_match(d, kag)
    P(f'\nmode={mode}: rebuilt rows {len(d)}; multiset match {m}; distinct tuples with different counts {ndiff}')
    if mode == 'pandas_round':
        best = (d, dia)
d, dia = best
P('\nResults (pandas_round build):')
P(' kept DIABETE3==2 (gestational only):', int((dia == 2).sum()))
P(' kept DIABETE3==4 (prediabetes):', int((dia == 4).sum()), '; Diabetes_012==1 in Kaggle:', int((kag.Diabetes_012 == 1).sum()))
P(' kept DIABETE3==1:', int((dia == 1).sum()), '; DIABETE3==3:', int((dia == 3).sum()))
P(' retention', len(d), '/', len(raw), '=', int(len(d) / len(raw) * 10000) / 10000, '(truncated)')
for c in kag.columns:
    if not (d[c].value_counts().sort_index().equals(kag[c].value_counts().sort_index())):
        P(' column marginal differs:', c)
out.close()
