"""P9 consequence layer, Q2 + Q3 (heart files). Follows prestated_rule_consequence.txt (sha256 dfcdd348...)."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import json, math, time
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score
from sklearn.inspection import permutation_importance
import lightgbm as lgb
import statsmodels.formula.api as smf

BASE = WORK_ROOT + '/consequence'
SEEDS = [20261125 + k for k in range(5)]
B = 200
t0 = time.time()

def t4(x):
    return math.trunc(x * 1e4) / 1e4 if x is not None and np.isfinite(x) else x

def log(*a):
    print(*a, flush=True)

def make(fam, cols, nums, seed):
    cats = [c for c in cols if c not in nums]
    nn = [c for c in cols if c in nums]
    if fam == 'LR':
        pre = ColumnTransformer([('c', OneHotEncoder(handle_unknown='ignore'), cats), ('n', StandardScaler(), nn)])
        est = LogisticRegression(C=1.0, solver='lbfgs', max_iter=3000)
    else:
        pre = ColumnTransformer([('c', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1), cats),
                                 ('n', 'passthrough', nn)])
        est = lgb.LGBMClassifier(n_estimators=100, learning_rate=0.1, num_leaves=31,
                                 random_state=seed, n_jobs=4, verbose=-1)
    return Pipeline([('pre', pre), ('m', est)])

def boot_diff(ya, pa, yb, pb):
    bs = np.random.RandomState(20261125)
    n = len(ya)
    d = []
    for _ in range(B):
        ii = bs.randint(0, n, n)
        d.append(roc_auc_score(ya[ii], pa[ii]) - roc_auc_score(yb[ii], pb[ii]))
    return [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]

def auc_rule(D, floor, ci):
    md = abs(float(np.median(D)))
    a, b, c = md >= 0.01, md > floor, (ci[0] > 0 or ci[1] < 0)
    if a and b and c:
        return 'MATERIAL'
    if (not a) and ci[0] > -0.01 and ci[1] < 0.01:
        return 'NOT MATERIAL'
    return 'INCONCLUSIVE'

# ------------------------------------------------------------------ 2022
d22 = pd.read_csv(f'{BASE}/work/2022/heart_2022_no_nans.csv')
nums22 = {'PhysicalHealthDays', 'MentalHealthDays', 'SleepHours', 'HeightInMeters', 'WeightInKilograms', 'BMI'}
yMI = (d22['HadHeartAttack'] == 'Yes').astype(int).values
yAN = (d22['HadAngina'] == 'Yes').astype(int).values
y20 = ((yMI + yAN) > 0).astype(int)
log('2022 rows', len(d22), 'MI', yMI.sum(), t4(yMI.mean()), 'y20', y20.sum(), t4(y20.mean()))
allc = [c for c in d22.columns if c != 'HadHeartAttack']
specs = {'M1': (allc, yMI), 'M2': ([c for c in allc if c != 'HadAngina'], yMI),
         'M3': ([c for c in allc if c != 'HadAngina'], y20)}
strat = yMI * 2 + yAN
res = {'rows22': len(d22), 'MI_pos': int(yMI.sum()), 'y20_pos': int(y20.sum()),
       'prev_MI': yMI.mean(), 'prev_y20': y20.mean(), 'seeds': {}}
boot = {}
for s in SEEDS:
    tr, te = train_test_split(np.arange(len(d22)), test_size=0.3, random_state=s, stratify=strat)
    sub = np.random.RandomState(s).choice(len(te), 30000, replace=False)
    r = {}
    for fam in ['LR', 'LGBM']:
        o = {}
        P = {}
        for name, (cols, y) in specs.items():
            m = make(fam, cols, nums22, s)
            m.fit(d22.iloc[tr][cols], y[tr])
            p = m.predict_proba(d22.iloc[te][cols])[:, 1]
            P[name] = p
            oo = {'auc_MI': roc_auc_score(yMI[te], p), 'auc_y20': roc_auc_score(y20[te], p)}
            if name == 'M1':
                pi = permutation_importance(m, d22.iloc[te].iloc[sub][cols], y[te][sub], scoring='roc_auc',
                                            n_repeats=5, random_state=s, n_jobs=1)
                imp = pi.importances_mean
                order = sorted(range(len(imp)), key=lambda i: (-imp[i], i))
                ia = cols.index('HadAngina')
                oo['angina_rank'] = order.index(ia) + 1
                pos = imp[imp > 0].sum()
                oo['angina_share'] = float(max(imp[ia], 0) / pos) if pos > 0 else None
                oo['top5'] = [(cols[i], float(imp[i])) for i in order[:5]]
            o[name] = oo
            log(f'2022 seed {s} {fam} {name} aucMI {t4(oo["auc_MI"])} aucY20 {t4(oo["auc_y20"])} '
                f'{oo.get("angina_rank","")} {time.time()-t0:.0f}s')
        r[fam] = o
        if s == SEEDS[0]:
            yt, y2 = yMI[te], y20[te]
            boot[fam] = {'D2_ci': boot_diff(yt, P['M1'], yt, P['M2']),
                         'D3_ci': boot_diff(y2, P['M3'], yt, P['M2'])}
    res['seeds'][str(s)] = r
res['boot_seed0'] = boot
summ = {}
for fam in ['LR', 'LGBM']:
    S = [res['seeds'][str(s)][fam] for s in SEEDS]
    m1 = [x['M1']['auc_MI'] for x in S]
    m2 = [x['M2']['auc_MI'] for x in S]
    m3 = [x['M3']['auc_y20'] for x in S]
    D2 = [a - b for a, b in zip(m1, m2)]
    D3 = [a - b for a, b in zip(m3, m2)]
    floor = max(m2) - min(m2)
    ranks = [x['M1']['angina_rank'] for x in S]
    shares = [x['M1']['angina_share'] for x in S]
    summ[fam] = {'M1': m1, 'M2': m2, 'M3': m3, 'M2_on_y20': [x['M2']['auc_y20'] for x in S],
                 'M3_on_MI': [x['M3']['auc_MI'] for x in S], 'D2': D2, 'D3': D3, 'floor': floor,
                 'D2_ci': boot[fam]['D2_ci'], 'D3_ci': boot[fam]['D3_ci'],
                 'v_D2': auc_rule(D2, floor, boot[fam]['D2_ci']), 'v_D3': auc_rule(D3, floor, boot[fam]['D3_ci']),
                 'angina_rank': ranks, 'angina_share': shares,
                 'angina_top': sum(r == 1 for r in ranks) >= 4 and float(np.median(shares)) >= 0.25,
                 'top5_seed0': S[0]['M1']['top5']}
v2a_parts = [summ[f]['v_D2'] for f in summ]
if 'MATERIAL' in v2a_parts or any(summ[f]['angina_top'] for f in summ):
    v2a = 'MATERIAL'
elif all(v == 'NOT MATERIAL' for v in v2a_parts) and all(1 not in summ[f]['angina_rank'] for f in summ):
    v2a = 'NOT MATERIAL'
else:
    v2a = 'INCONCLUSIVE'
v3 = [summ[f]['v_D3'] for f in summ]
v2b = 'MATERIAL' if 'MATERIAL' in v3 else ('NOT MATERIAL' if all(v == 'NOT MATERIAL' for v in v3) else 'INCONCLUSIVE')
res['summary22'] = summ
res['verdict'] = {'Q2a': v2a, 'Q2b': v2b}
log(json.dumps(res['verdict']))

# ------------------------------------------------------------------ 2020 descriptive
d20 = pd.read_csv(f'{BASE}/work/2020/heart_2020_cleaned.csv')
y = (d20['HeartDisease'] == 'Yes').astype(int).values
cols20 = [c for c in d20.columns if c != 'HeartDisease']
nums20 = {'BMI', 'PhysicalHealth', 'MentalHealth', 'SleepTime'}
a20 = {'LR': [], 'LGBM': []}
for s in SEEDS:
    tr, te = train_test_split(np.arange(len(d20)), test_size=0.3, random_state=s, stratify=y)
    for fam in a20:
        m = make(fam, cols20, nums20, s)
        m.fit(d20.iloc[tr][cols20], y[tr])
        a20[fam].append(roc_auc_score(y[te], m.predict_proba(d20.iloc[te][cols20])[:, 1]))
    log('2020 seed', s, {k: t4(v[-1]) for k, v in a20.items()}, f'{time.time()-t0:.0f}s')
res['auc2020'] = a20
res['prev2020'] = y.mean()

# ------------------------------------------------------------------ Q3 alcohol
def orfit(df, ycol, acol, ageref, adj):
    f = f'{ycol} ~ {acol}' + (f' + C(AgeCategory, Treatment(reference="{ageref}")) + C(Sex)' if adj else '')
    m = smf.logit(f, data=df).fit(disp=0, maxiter=200)
    b, ci = m.params[acol], m.conf_int().loc[acol]
    return {'OR': math.exp(b), 'lo': math.exp(ci[0]), 'hi': math.exp(ci[1]), 'p': float(m.pvalues[acol])}

q3 = {}
e20 = pd.DataFrame({'y': y, 'alc': (d20['AlcoholDrinking'] == 'Yes').astype(int),
                    'AgeCategory': d20['AgeCategory'], 'Sex': d20['Sex']})
e22 = pd.DataFrame({'y': yMI, 'y20': y20, 'alc': (d22['AlcoholDrinkers'] == 'Yes').astype(int),
                    'AgeCategory': d22['AgeCategory'], 'Sex': d22['Sex']})
for nm, e, yc, ref in [('2020_HeartDisease', e20, 'y', '18-24'), ('2022_HadHeartAttack', e22, 'y', 'Age 18 to 24'),
                       ('2022_y20', e22, 'y20', 'Age 18 to 24')]:
    q = {'alc_yes_share': e['alc'].mean(), 'rate_yes': e.loc[e.alc == 1, yc].mean(),
         'rate_no': e.loc[e.alc == 0, yc].mean(), 'n_yes': int(e['alc'].sum()), 'n': len(e)}
    q['crude'] = orfit(e, yc, 'alc', ref, False)
    q['adj'] = orfit(e, yc, 'alc', ref, True)
    q3[nm] = q
    log('Q3', nm, {k: (t4(v) if isinstance(v, float) else v) for k, v in q.items() if not isinstance(v, dict)},
        'crude', {k: t4(v) for k, v in q['crude'].items()}, 'adj', {k: t4(v) for k, v in q['adj'].items()})
a, b = q3['2020_HeartDisease']['adj'], q3['2022_HadHeartAttack']['adj']
nonoverlap = a['hi'] < b['lo'] or b['hi'] < a['lo']
flip = False
for nm in ['2020_HeartDisease', '2022_HadHeartAttack']:
    c, d = q3[nm]['crude'], q3[nm]['adj']
    excl = lambda z: z['lo'] > 1 or z['hi'] < 1
    if excl(c) and excl(d) and ((c['OR'] - 1) * (d['OR'] - 1) < 0):
        flip = True
q3['nonoverlap'] = nonoverlap
q3['signflip'] = flip
res['q3'] = q3
res['verdict']['Q3'] = 'MATERIAL' if (nonoverlap or flip) else 'NOT MATERIAL'
log(json.dumps(res['verdict']))
for f in summ:
    log(f, summ[f])
with open(f'{BASE}/out/q2q3_heart.json', 'w', encoding='utf-8') as fh:
    json.dump(res, fh, indent=1, default=float)
log('done', f'{time.time()-t0:.0f}s')
