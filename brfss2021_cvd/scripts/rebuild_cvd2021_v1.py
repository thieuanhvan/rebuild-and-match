"""I360 rebuild pilot v1: CVD_cleaned.csv (alphiree) from raw BRFSS 2021 LLCP.
Hypothesis H1 for consumption items: 1xx -> xx*30 per month, 2xx -> xx*4, 3xx -> xx, 300 -> 0, 555 -> 0.
Alcohol: ALCDAY5 1xx (days/week) -> xx*4, 2xx (days/30) -> xx, 888 -> 0.
Compares marginal distributions, then multiset over all 19 columns."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import sys, zipfile, collections
import numpy as np, pandas as pd
W = WORK_ROOT + '/brfss2021_cvd/'
K = SURVEY_DATA_ROOT + '/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip'
r = pd.read_pickle(W + 'raw2021_sub.pkl')
k = pd.read_csv(zipfile.ZipFile(K).open('CVD_cleaned.csv'))

def yn(s):
    return s.map({1: 'Yes', 2: 'No'})

def cons(s, day=30, wk=4):
    out = pd.Series(np.nan, index=s.index)
    d = (s > 100) & (s < 200); w = (s > 200) & (s < 300); m = (s > 300) & (s < 400)
    out[d] = (s[d] - 100) * day; out[w] = (s[w] - 200) * wk; out[m] = s[m] - 300
    out[(s == 300) | (s == 555)] = 0
    return out

def alc(s):
    out = pd.Series(np.nan, index=s.index)
    w = (s > 100) & (s < 200); m = (s > 200) & (s < 300)
    out[w] = (s[w] - 100) * 4; out[m] = s[m] - 200; out[s == 888] = 0
    return out

b = pd.DataFrame(index=r.index)
b['General_Health'] = r.GENHLTH.map({1: 'Excellent', 2: 'Very Good', 3: 'Good', 4: 'Fair', 5: 'Poor'})
b['Checkup'] = r.CHECKUP1.map({1: 'Within the past year', 2: 'Within the past 2 years', 3: 'Within the past 5 years', 4: '5 or more years ago', 8: 'Never'})
b['Exercise'] = yn(r.EXERANY2)
b['Heart_Disease'] = yn(r._MICHD)
b['Skin_Cancer'] = yn(r.CHCSCNCR)
b['Other_Cancer'] = yn(r.CHCOCNCR)
b['Depression'] = yn(r.ADDEPEV3)
b['Diabetes'] = r.DIABETE4.map({1: 'Yes', 2: 'Yes, but female told only during pregnancy', 3: 'No', 4: 'No, pre-diabetes or borderline diabetes'})
b['Arthritis'] = yn(r.HAVARTH5)
b['Sex'] = r.SEXVAR.map({1: 'Male', 2: 'Female'})
ages = ['18-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80+']
b['Age_Category'] = r._AGEG5YR.map({i + 1: a for i, a in enumerate(ages)})
b['Height_(cm)'] = r.HTM4
b['Weight_(kg)'] = r.WTKG3 / 100
b['BMI'] = r._BMI5 / 100
b['Smoking_History'] = yn(r.SMOKE100)
b['Alcohol_Consumption'] = alc(r.ALCDAY5)
b['Fruit_Consumption'] = cons(r.FRUIT2)
b['Green_Vegetables_Consumption'] = cons(r.FVGREEN1)
b['FriedPotato_Consumption'] = cons(r.FRENCHF1)
print('raw', len(b), 'complete cases H1', b.dropna().shape[0], 'kaggle', len(k))
cc = b.dropna()
for c in k.columns:
    kv = k[c].value_counts(); bv = cc[c].value_counts()
    if k[c].dtype == object:
        diff = (kv - bv.reindex(kv.index).fillna(0)).abs().sum()
        print(f'{c}: kaggle vs rebuild abs diff {int(diff)}')
    else:
        print(f'{c}: kaggle min/max {k[c].min()}/{k[c].max()} n_unique {k[c].nunique()} | rebuild {cc[c].min()}/{cc[c].max()} n_unique {cc[c].nunique()}')
cc.to_pickle(W + 'rebuild_h1_cc.pkl'); b.to_pickle(W + 'rebuild_h1_all.pkl')
