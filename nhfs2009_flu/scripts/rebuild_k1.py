"""Rebuild the Flu Shot Learning features from NHFS 2009-10 adults and match against the Kaggle copy.
Usage: python -I -X utf8 rebuild_k1.py"""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import os, psutil, collections
import numpy as np, pandas as pd
psutil.Process(os.getpid()).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
W = WORK_ROOT + '/nhfs2009_flu/'
K = SURVEY_DATA_ROOT + '/flushot-kaggle/raw/'
d = pd.read_pickle(W + 'nhfs_raw.pkl')
a = d[d.SUBGROUP == 'A'].copy()
print('adults', len(a))
tr = pd.read_csv(K + 'training_set_features.csv'); te = pd.read_csv(K + 'test_set_features.csv')
lab = pd.read_csv(K + 'training_set_labels.csv')
k = pd.concat([tr, te], ignore_index=True)
print('kaggle train', len(tr), 'test', len(te), 'total', len(k))

def flag(s):
    return s.where(s.isin([0, 1]))
def onehot(df, levels):  # levels: list of (col, value); NaN if none set
    out = pd.Series(np.nan, index=df.index)
    for c, v in levels:
        out[df[c] == 1] = v
    return out
r = pd.DataFrame(index=a.index)
r['h1n1_concern'] = onehot(a, [('CONCERN_NONE_F', 0), ('CONCERN_NOTV_F', 1), ('CONCERN_SOME_F', 2), ('CONCERN_VERY_F', 3)])
r['h1n1_knowledge'] = onehot(a, [('KNOW_H1N1_NONE_F', 0), ('KNOW_H1N1_LITL_F', 1), ('KNOW_H1N1_ALOT_F', 2)])
for c, n in [('B_H1N1_ANTIV', 'antiviral_meds'), ('B_H1N1_AVOID', 'avoidance'), ('B_H1N1_FMASK', 'face_mask'), ('B_H1N1_HANDS', 'wash_hands'),
             ('B_H1N1_LARGE', 'large_gatherings'), ('B_H1N1_RCONT', 'outside_home'), ('B_H1N1_TOUCH', 'touch_face')]:
    r['behavioral_' + n] = flag(a[c])
valid_doc = (a[['DOCREC_BOTH_F', 'DOCREC_H1N1_F', 'DOCREC_SEAS_F', 'DOCREC_NTHR_F']] == 1).any(axis=1)
r['doctor_recc_h1n1'] = np.where(valid_doc, ((a.DOCREC_H1N1_F == 1) | (a.DOCREC_BOTH_F == 1)).astype(float), np.nan)
r['doctor_recc_seasonal'] = np.where(valid_doc, ((a.DOCREC_SEAS_F == 1) | (a.DOCREC_BOTH_F == 1)).astype(float), np.nan)
r['chronic_med_condition'] = flag(a.CHRONIC_MED_F)
r['child_under_6_months'] = flag(a.CLOSE_UNDER6MO_F)
r['health_worker'] = flag(a.HEALTH_WORKER_F)
r['health_insurance'] = a.INSURE.map({'01': 1.0, '02': 0.0})
DK = 3.0  # hypothesis h2: "don't know" placed at the midpoint
op_eff = {'04': 1.0, '03': 2.0, '77': DK, '02': 4.0, '01': 5.0}
for c, n in [('HQ23', 'opinion_h1n1_vacc_effective'), ('HQ24', 'opinion_h1n1_risk'), ('HQ24_B', 'opinion_h1n1_sick_from_vacc'),
             ('Q23', 'opinion_seas_vacc_effective'), ('Q24', 'opinion_seas_risk'), ('Q24_B', 'opinion_seas_sick_from_vacc')]:
    r[n] = a[c].map(op_eff)
r['age_group'] = a.AGEGRP.map({3: '18 - 34 Years', 4: '35 - 44 Years', 5: '45 - 54 Years', 6: '55 - 64 Years', 7: '65+ Years'})
r['education'] = a.EDUCATION_COMP.map({1: '< 12 Years', 2: '12 Years', 3: 'Some College', 4: 'College Graduate'})
r['race'] = a.RACEETH4_I.map({1: 'Hispanic', 2: 'Black', 3: 'White', 4: 'Other or Multiple'})
r['sex'] = a.SEX_I.map({1: 'Male', 2: 'Female'})
r['income_poverty'] = a.INC_POV.map({1: '> $75,000', 2: '<= $75,000, Above Poverty', 3: 'Below Poverty'})
r['marital_status'] = a.MARITAL.map({1: 'Married', 2: 'Not Married'})
r['rent_or_own'] = a.RENT_OWN_R.map({'01': 'Own', '02': 'Rent'})
r['employment_status'] = a.Q95.map({'01': 'Employed', '02': 'Unemployed', '03': 'Not in Labor Force'})
r['census_msa'] = a.MSA3_I.map({1: 'MSA, Principle City', 2: 'MSA, Not Principle  City', 3: 'Non-MSA'})
r['household_adults'] = (a.N_ADULT_R - 1).clip(upper=3)
r['household_children'] = a.HH_CHILD_R.clip(upper=3)
r['_region'] = a.HHS_REGION; r['_ind'] = a.Q95_INDSTR; r['_occ'] = a.Q95_OCCPN
r['h1n1_vaccine'] = flag(a.VACC_H1N1_F); r['seasonal_vaccine'] = flag(a.VACC_SEAS_F)
r['INT_MONTH'] = a.INT_MONTH; r['FLUWT'] = a.FLUWT; r['STATE'] = a.STATE
r.to_pickle(W + 'k1_rebuild.pkl')

# marginal comparison (adults vs kaggle train+test)
plain = [c for c in tr.columns if c not in ('respondent_id', 'hhs_geo_region', 'employment_industry', 'employment_occupation')]
print('\n== marginals: column, kaggle counts vs rebuild counts (all adults) ==')
for c in plain:
    kc = k[c].value_counts(dropna=False).sort_index().to_dict(); rc = r[c].value_counts(dropna=False).sort_index().to_dict()
    print(c, '\n  K', kc, '\n  R', rc)
print('labels missing in rebuild:', r.h1n1_vaccine.isna().sum(), r.seasonal_vaccine.isna().sum())
