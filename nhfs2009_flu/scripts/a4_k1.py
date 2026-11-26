"""K1 A4 consequence analysis under consequence/a4_rule_k1.txt. Usage: python -I -X utf8 a4_k1.py"""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import os, psutil, warnings
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_v] = '1'  # run 1 gave a nondeterministic logistic fit; single-threaded BLAS for reproducibility
import numpy as np, pandas as pd
psutil.Process(os.getpid()).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
warnings.filterwarnings('ignore')
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import roc_auc_score
import lightgbm as lgb
import statsmodels.api as sm

W = WORK_ROOT + '/nhfs2009_flu/'
K = SURVEY_DATA_ROOT + '/flushot-kaggle/raw/'


def t4(x):
    return int(x * 10000) / 10000 if x >= 0 else -int(-x * 10000) / 10000


lk = pd.read_pickle(W + 'k1_linked.pkl')
tr = pd.read_csv(K + 'training_set_features.csv').merge(pd.read_csv(K + 'training_set_labels.csv'), on='respondent_id')
feats = [c for c in tr.columns if c not in ('respondent_id', 'h1n1_vaccine', 'seasonal_vaccine')]
plain = [c for c in feats if c not in ('hhs_geo_region', 'employment_industry', 'employment_occupation')]
tr['_key'] = [tuple('NA' if pd.isna(v) else v for v in row) for row in tr[plain].itertuples(index=False)]
m = lk[lk._set == 'train'][['_key', 'INT_MONTH', 'FLUWT', 'h1n1_vaccine', 'seasonal_vaccine']]
m = m.rename(columns={'h1n1_vaccine': 'n_h1', 'seasonal_vaccine': 'n_se'})
T = tr.merge(m, on='_key', how='inner').reset_index(drop=True)
print('T rows', len(T), 'of train', len(tr), '; label agreement h1n1', (T.n_h1 == T.h1n1_vaccine).mean(),
      'seasonal', (T.n_se == T.seasonal_vaccine).mean())
cat = [c for c in feats if T[c].dtype == object]
num = [c for c in feats if c not in cat]
op = [c for c in feats if c.startswith('opinion_')]
for c in op:
    T[c + '_dk'] = (T[c] == 3).astype(float)
    T[c + '_x'] = T[c].where(T[c] != 3)


def design(df, numc, catc, ref):
    X = pd.DataFrame(index=df.index)
    for c in numc:
        X[c] = df[c].fillna(ref[c].median())
        X[c + '_na'] = df[c].isna().astype(float)
    D = pd.get_dummies(df[catc].fillna('NA').astype(str), dtype=float)
    return pd.concat([X, D], axis=1)


def lr_pair(numc, catc):
    def f(a, b):
        A = design(a, numc, catc, a)
        B = design(b, numc, catc, a).reindex(columns=A.columns, fill_value=0)
        return A, B
    return f


def lgb_pair(cols):
    def f(a, b):
        out = []
        for df in (a, b):
            X = df[cols].copy()
            for c in cols:
                if X[c].dtype == object:
                    X[c] = pd.Categorical(X[c], categories=sorted(T[c].dropna().unique()))
            out.append(X)
        return out
    return f


def predict(model, Xtr, ytr, Xte):
    if model == 'lr':
        mu, sd = Xtr.mean(), Xtr.std().replace(0, 1)
        clf = LogisticRegression(C=1, max_iter=3000).fit((Xtr - mu) / sd, ytr)
        return clf.predict_proba((Xte - mu) / sd)[:, 1]
    clf = lgb.LGBMClassifier(n_estimators=100, learning_rate=0.1, num_leaves=31, verbose=-1).fit(Xtr, ytr)
    return clf.predict_proba(Xte)[:, 1]


SPLITS = [next(StratifiedShuffleSplit(n_splits=1, test_size=0.3, random_state=s).split(T, T.h1n1_vaccine)) for s in range(5)]


def compare(name, model, pair_a, pair_b, target):
    diffs = []
    first = None
    for s, (i, j) in enumerate(SPLITS):
        a, b = T.iloc[i], T.iloc[j]
        ytr, yte = a[target].values, b[target].values
        Atr, Ate = pair_a(a, b)
        Btr, Bte = pair_b(a, b)
        pa, pb = predict(model, Atr, ytr, Ate), predict(model, Btr, ytr, Bte)
        aa, ab = roc_auc_score(yte, pa), roc_auc_score(yte, pb)
        diffs.append(ab - aa)
        if s == 0:
            first = (yte, pa, pb, aa, ab)
    y, pa, pb, aa, ab = first
    rng = np.random.default_rng(0)
    bs = []
    for _ in range(200):
        k = rng.integers(0, len(y), len(y))
        bs.append(roc_auc_score(y[k], pb[k]) - roc_auc_score(y[k], pa[k]))
    lo, hi = np.percentile(bs, [2.5, 97.5])
    med = float(np.median(diffs))
    mat = med >= 0.01 and min(diffs) > 0 and lo > 0
    notm = abs(med) < 0.01 and lo > -0.01 and hi < 0.01
    verdict = 'MATERIAL' if mat else ('not material' if notm else 'indeterminate')
    print(f'{name} | {target} | {model}: AUC A {t4(aa)} B {t4(ab)} (split 0); median diff {t4(med)}; '
          f'range [{t4(min(diffs))}, {t4(max(diffs))}]; CI [{t4(lo)}, {t4(hi)}]; {verdict}')


print('\n== Q1 timing: features + INT_MONTH minus features ==')
for tgt in ('h1n1_vaccine', 'seasonal_vaccine'):
    compare('Q1', 'lr', lr_pair(num, cat), lr_pair(num, cat + ['INT_MONTH']), tgt)
    compare('Q1', 'lgb', lgb_pair(feats), lgb_pair(feats + ['INT_MONTH']), tgt)

print('\n== Q3 dont-know at the midpoint (LR): distributed minus DK as indicator, reported as B - A with B = DK indicator ==')
num_b = [c for c in num if c not in op] + [c + '_x' for c in op] + [c + '_dk' for c in op]
for tgt in ('h1n1_vaccine', 'seasonal_vaccine'):
    compare('Q3', 'lr', lr_pair(num, cat), lr_pair(num_b, cat), tgt)

print('\n== Q2 odds ratios for h1n1_vaccine, adjusted for age and sex, without vs with INT_MONTH ==')
for v in ('doctor_recc_h1n1', 'chronic_med_condition', 'health_insurance'):
    sub = T[[v, 'age_group', 'sex', 'INT_MONTH', 'h1n1_vaccine']].dropna()
    res = {}
    for lab, cols in (('without', ['age_group', 'sex']), ('with', ['age_group', 'sex', 'INT_MONTH'])):
        X = pd.concat([sub[[v]].astype(float), pd.get_dummies(sub[cols], drop_first=True, dtype=float)], axis=1)
        fit = sm.Logit(sub.h1n1_vaccine.astype(float), sm.add_constant(X)).fit(disp=0)
        b, se = fit.params[v], fit.bse[v]
        res[lab] = (np.exp(b), np.exp(b - 1.96 * se), np.exp(b + 1.96 * se))
    (o1, l1, h1), (o2, l2, h2) = res['without'], res['with']
    mat = (h1 < l2 or h2 < l1) or ((o1 - 1) * (o2 - 1) < 0)
    print(f'{v} (n={len(sub)}): without month OR {t4(o1)} [{t4(l1)}, {t4(h1)}]; with month OR {t4(o2)} '
          f'[{t4(l2)}, {t4(h2)}]; ' + ('MATERIAL' if mat else 'not material'))

print('\n== Q4 descriptive ==')
early = T.INT_MONTH.isin(['OCT09', 'NOV09', 'DEC09']).astype(int)
Xm = pd.DataFrame({'hi_na': T.health_insurance.isna().astype(float), 'dr_na': T.doctor_recc_h1n1.isna().astype(float)})
p = LogisticRegression().fit(Xm, early).predict_proba(Xm)[:, 1]
print('AUC predicting OCT-DEC 2009 interview from two missing indicators (in-sample):', t4(roc_auc_score(early, p)))
print('share early', t4(early.mean()))
for tgt in ('h1n1_vaccine', 'seasonal_vaccine'):
    w = T.FLUWT
    print(tgt, 'unweighted', t4(T[tgt].mean()), 'weighted', t4((T[tgt] * w).sum() / w.sum()))
