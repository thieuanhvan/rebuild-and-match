"""verify3 2015: weighted prevalences + Taylor SE, exclusion arithmetic, duplicate counts in Kaggle diabetes files."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np
from svy import report, tr4
V3 = WORK_ROOT + '/verify3'
K = SURVEY_DATA_ROOT + '/kaggle-diabetes-2015'
out = open(f'{V3}/w2015_out.txt', 'w', encoding='utf-8')
def P(*a):
    print(*a); print(*a, file=out, flush=True)

raw = pd.read_parquet(f'{V3}/raw/raw2015.parquet')
k012 = pd.read_csv(f'{K}/diabetes_012_health_indicators_BRFSS2015.csv')
kbin = pd.read_csv(f'{K}/diabetes_binary_health_indicators_BRFSS2015.csv')
k55 = pd.read_csv(f'{K}/diabetes_binary_5050split_health_indicators_BRFSS2015.csv')
P('raw rows', len(raw), '; weight NaN', int(raw._LLCPWT.isna().sum()), 'strata NaN', int(raw._STSTR.isna().sum()), 'psu NaN', int(raw._PSU.isna().sum()))

# rebuild (same rules as verify2/tools/a_rebuild2015.py, pandas half-to-even BMI rounding)
feat = ['DIABETE3', '_RFHYPE5', 'TOLDHI2', '_CHOLCHK', '_BMI5', 'SMOKE100', 'CVDSTRK3', '_MICHD', '_TOTINDA',
        '_FRTLT1', '_VEGLT1', '_RFDRHV5', 'HLTHPLN1', 'MEDCOST', 'GENHLTH', 'MENTHLTH', 'PHYSHLTH', 'DIFFWALK',
        'SEX', '_AGEG5YR', 'EDUCA', 'INCOME2']
d = raw[feat].dropna().copy()
d = d[~d.DIABETE3.isin([7, 9])]
d['DIABETE3'] = d.DIABETE3.map({1: 2, 2: 0, 3: 0, 4: 1})
d = d[d._RFHYPE5 != 9]; d['_RFHYPE5'] = d._RFHYPE5.map({1: 0, 2: 1})
d = d[~d.TOLDHI2.isin([7, 9])]; d['TOLDHI2'] = d.TOLDHI2.map({1: 1, 2: 0})
d = d[d._CHOLCHK != 9]; d['_CHOLCHK'] = d._CHOLCHK.map({1: 1, 2: 0, 3: 0})
d['_BMI5'] = (d._BMI5 / 100).round(0)
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
d.columns = list(k012.columns)
d = d.astype(float)
ca, cb = d.value_counts(), k012.value_counts()
j = pd.concat([ca.rename('a'), cb.rename('b')], axis=1).fillna(0)
P('rebuild rows', len(d), '; multiset match vs Kaggle 012', np.minimum(j.a, j.b).sum() / len(k012), '; differing tuples', int((j.a != j.b).sum()))

dia = raw.DIABETE3
valid = dia.isin([1, 2, 3, 4])
cc = pd.Series(False, index=raw.index); cc.loc[d.index] = True
P('\nDIABETE3 codes', dict(dia.value_counts(dropna=False).sort_index()))
P('valid diabetes answer (1-4):', int(valid.sum()), '; excluded for label:', len(raw) - int(valid.sum()))
P('excluded by complete-case among valid:', int(valid.sum()) - len(d))
P('complete-case rows', len(d), 'share of raw', tr4(len(d) / len(raw)))
y1 = (dia == 1).astype(float); ydoc = dia.isin([1, 4]).astype(float)
w, h, c = raw._LLCPWT.values, raw._STSTR.values, raw._PSU.values
P('\nWeighted (weight _LLCPWT, strata _STSTR, PSU _PSU nested in strata; Taylor, with replacement)')
report(P, 'diabetes (DIABETE3=1), all valid respondents', y1, w, h, c, valid.values)
report(P, 'diabetes (DIABETE3=1), complete-case population', y1, w, h, c, cc.values)
report(P, 'documented label (DIABETE3 in 1,4), all valid', ydoc, w, h, c, valid.values)
report(P, 'documented label (DIABETE3 in 1,4), complete-case population', ydoc, w, h, c, cc.values)
P('check: complete-case DIABETE3=1 count', int(y1[cc].sum()), '; =4 count', int((dia[cc] == 4).sum()), '; =2 count', int((dia[cc] == 2).sum()))

P('\nKaggle files')
for name, f in [('012', k012), ('binary', kbin), ('5050', k55)]:
    nd = int(f.duplicated().sum())
    P(f' {name}: rows {len(f)}, exact duplicate rows beyond first {nd}, share {tr4(nd / len(f))}')
P(' binary class 1:', int((kbin.Diabetes_binary == 1).sum()), 'unweighted rate', tr4((kbin.Diabetes_binary == 1).mean()))
P(' rebuild duplicates (012 coding):', int(d.duplicated().sum()))
P(' 24206/253680 =', 24206 / 253680, '-> trunc', tr4(24206 / 253680))
P(' 440658-253680 =', 440658 - 253680)
out.close()
