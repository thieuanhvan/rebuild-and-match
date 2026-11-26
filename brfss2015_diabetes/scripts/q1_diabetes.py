"""P9 consequence layer, Q1 (diabetes file). Follows prestated_rule_consequence.txt (sha256 dfcdd348...)."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import json, math, sys, time
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score
from sklearn.inspection import permutation_importance
from scipy.stats import kendalltau
import lightgbm as lgb

C = WORK_ROOT + '/consequence'
F = SURVEY_DATA_ROOT + '/kaggle-diabetes-2015/diabetes_012_health_indicators_BRFSS2015.csv'
SEEDS = [20261125 + k for k in range(5)]
B = 200

def t4(x):
    return math.trunc(x * 1e4) / 1e4 if x is not None and np.isfinite(x) else x

def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (None, None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, c - h, c + h)

def models(seed):
    return {
        'LR': make_pipeline(StandardScaler(), LogisticRegression(C=1.0, solver='lbfgs', max_iter=3000)),
        'LGBM': lgb.LGBMClassifier(n_estimators=100, learning_rate=0.1, num_leaves=31,
                                   random_state=seed, n_jobs=4, verbose=-1),
    }

def log(*a):
    print(*a, flush=True)

t0 = time.time()
df = pd.read_csv(F)
y012 = df['Diabetes_012'].astype(int).values
X = df.drop(columns=['Diabetes_012']).astype(float)
feats = list(X.columns)
yA = (y012 == 2).astype(int)
yD = (y012 >= 1).astype(int)
log('rows', len(df), 'n012', np.bincount(y012).tolist(), 'prevA', t4(yA.mean()), 'prevD', t4(yD.mean()))

res = {'rows': len(df), 'n012': np.bincount(y012).tolist(), 'prevA': yA.mean(), 'prevD': yD.mean(), 'seeds': {}}
boot = {}
for s in SEEDS:
    idx = np.arange(len(df))
    tr, te = train_test_split(idx, test_size=0.3, random_state=s, stratify=y012)
    Xtr, Xte = X.iloc[tr], X.iloc[te]
    r = {}
    rng = np.random.RandomState(s)
    sub = rng.choice(len(te), 30000, replace=False)
    for fam in ['LR', 'LGBM']:
        out = {}
        preds = {}
        for lab, y in [('A', yA), ('D', yD)]:
            m = models(s)[fam]
            m.fit(Xtr, y[tr])
            ptr = m.predict_proba(Xtr)[:, 1]
            pte = m.predict_proba(Xte)[:, 1]
            preds[lab] = pte
            ptrain = y[tr].mean()
            t2 = float(np.quantile(ptr, 1 - ptrain))
            o = {'auc_on_A': roc_auc_score(yA[te], pte), 'auc_on_D': roc_auc_score(yD[te], pte),
                 'mean_pred': pte.mean(), 'citl_vs_A': pte.mean() - yA[te].mean(),
                 'citl_vs_D': pte.mean() - yD[te].mean(), 't2': t2}
            for tn, thr in [('t1', 0.5), ('t2', t2)]:
                fl = pte >= thr
                g = {}
                for gname, mask in [('pre', y012[te] == 1), ('dia', y012[te] == 2), ('no', y012[te] == 0),
                                    ('preordia', y012[te] >= 1)]:
                    k, n = int(fl[mask].sum()), int(mask.sum())
                    p, lo, hi = wilson(k, n)
                    g[gname] = {'k': k, 'n': n, 'p': p, 'lo': lo, 'hi': hi}
                g['flag_share'] = fl.mean()
                o[tn] = g
            pi = permutation_importance(m, Xte.iloc[sub], y[te][sub], scoring='roc_auc', n_repeats=5,
                                        random_state=s, n_jobs=1)
            o['perm'] = pi.importances_mean.tolist()
            out[lab] = o
            log(f'seed {s} {fam} {lab} aucA {t4(o["auc_on_A"])} aucD {t4(o["auc_on_D"])} '
                f'pre_t1 {t4(o["t1"]["pre"]["p"])} pre_t2 {t4(o["t2"]["pre"]["p"])} '
                f'dia_t2 {t4(o["t2"]["dia"]["p"])} {time.time()-t0:.0f}s')
        r[fam] = out
        if s == SEEDS[0]:
            bs = np.random.RandomState(20261125)
            n = len(te)
            d = []
            ya, yd = yA[te], yD[te]
            for b in range(B):
                ii = bs.randint(0, n, n)
                d.append(roc_auc_score(yd[ii], preds['D'][ii]) - roc_auc_score(ya[ii], preds['A'][ii]))
            boot[fam] = {'D1_ci': [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]}
    res['seeds'][str(s)] = r

res['boot_seed0'] = boot
res['features'] = feats

def ranks(imp):
    order = sorted(range(len(imp)), key=lambda i: (-imp[i], i))
    return order

summ = {}
for fam in ['LR', 'LGBM']:
    S = [res['seeds'][str(s)][fam] for s in SEEDS]
    aucAA = [x['A']['auc_on_A'] for x in S]
    aucDD = [x['D']['auc_on_D'] for x in S]
    D1 = [d - a for d, a in zip(aucDD, aucAA)]
    ov_AD, tau_AD, ov_AA = [], [], []
    for x in S:
        ra, rd = ranks(x['A']['perm']), ranks(x['D']['perm'])
        ov_AD.append(len(set(ra[:10]) & set(rd[:10])))
        tau_AD.append(kendalltau(x['A']['perm'], x['D']['perm']).statistic)
    for k in range(4):
        ra, rb = ranks(S[k]['A']['perm']), ranks(S[k + 1]['A']['perm'])
        ov_AA.append(len(set(ra[:10]) & set(rb[:10])))
    floor = max(aucAA) - min(aucAA)
    q1b_a = abs(np.median(D1)) >= 0.01
    q1b_b = abs(np.median(D1)) > floor
    ci = boot[fam]['D1_ci']
    q1b_c = ci[0] > 0 or ci[1] < 0
    if q1b_a and q1b_b and q1b_c:
        v1b = 'MATERIAL'
    elif (not q1b_a) and ci[0] > -0.01 and ci[1] < 0.01:
        v1b = 'NOT MATERIAL'
    else:
        v1b = 'INCONCLUSIVE'
    # Q1a
    cond_i = all(x[lab][tn]['pre']['hi'] < x[lab][tn]['dia']['lo'] for x in S for lab in ['A'] for tn in ['t1', 't2'])
    sensdiff = [x['A']['t2']['dia']['p'] - x['A']['t2']['preordia']['p'] for x in S]
    cond_ii = all(d >= 0.02 for d in sensdiff)
    citlAD = [x['A']['citl_vs_D'] for x in S]
    medov = float(np.median(ov_AD))
    if medov < 7 and medov < min(ov_AA):
        v1d = 'MATERIAL'
    elif medov >= 8 or medov >= min(ov_AA):
        v1d = 'NOT MATERIAL'
    else:
        v1d = 'INCONCLUSIVE'
    summ[fam] = {'aucAA': aucAA, 'aucDD': aucDD, 'aucAD': [x['A']['auc_on_D'] for x in S],
                 'aucDA': [x['D']['auc_on_A'] for x in S], 'D1': D1, 'floor': floor, 'D1_ci': ci,
                 'v1b': v1b, 'cond_i': cond_i, 'cond_ii': cond_ii, 'sensdiff_t2': sensdiff,
                 'citl_A_vs_D': citlAD, 'citl_A_vs_A': [x['A']['citl_vs_A'] for x in S],
                 'citl_D_vs_D': [x['D']['citl_vs_D'] for x in S],
                 'v1c': 'MATERIAL' if all(abs(c) >= 0.01 for c in citlAD) else 'NOT MATERIAL',
                 'ov_AD': ov_AD, 'tau_AD': tau_AD, 'ov_AA': ov_AA, 'v1d': v1d,
                 'top10_A_seed0': [feats[i] for i in ranks(S[0]['A']['perm'])[:10]],
                 'top10_D_seed0': [feats[i] for i in ranks(S[0]['D']['perm'])[:10]]}
res['summary'] = summ
ci_all = all(summ[f]['cond_i'] for f in summ)
cii_all = all(summ[f]['cond_ii'] for f in summ)
res['verdict'] = {
    'Q1a': 'MATERIAL' if ci_all and cii_all else ('NOT MATERIAL' if not ci_all and not cii_all else 'INCONCLUSIVE'),
    'Q1b': 'MATERIAL' if 'MATERIAL' in [summ[f]['v1b'] for f in summ] else (
        'NOT MATERIAL' if all(summ[f]['v1b'] == 'NOT MATERIAL' for f in summ) else 'INCONCLUSIVE'),
    'Q1c': 'MATERIAL' if all(summ[f]['v1c'] == 'MATERIAL' for f in summ) else 'NOT MATERIAL',
    'Q1d': 'MATERIAL' if 'MATERIAL' in [summ[f]['v1d'] for f in summ] else (
        'NOT MATERIAL' if all(summ[f]['v1d'] == 'NOT MATERIAL' for f in summ) else 'INCONCLUSIVE'),
}
log(json.dumps(res['verdict']))
for f in summ:
    log(f, {k: v for k, v in summ[f].items()})
with open(f'{C}/out/q1_diabetes.json', 'w', encoding='utf-8') as fh:
    json.dump(res, fh, indent=1, default=float)
log('done', f'{time.time()-t0:.0f}s')
