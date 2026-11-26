"""I360 A4 consequence analysis, following consequence/a4_rule_i360.txt (sha256 d9810b62...53ef).
Usage: python -I -X utf8 consequence/a4_i360.py"""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import os, time
import numpy as np, pandas as pd, psutil
psutil.Process(os.getpid()).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score
import lightgbm as lgb
import statsmodels.api as sm

W = WORK_ROOT + '/brfss2021_cvd/'
t4 = lambda x: int(x * 10000) / 10000 if x >= 0 else -int(-x * 10000) / 10000
r = pd.read_pickle(W + 'raw2021_sub.pkl')
b0 = pd.read_pickle(W + 'rebuild_h1_all.pkl')
Ff = pd.read_pickle(W + 'rebuild_exact_cc.pkl')          # file rows, file coding (exact Kaggle multiset)
FC = {'Fruit_Consumption': 'FRUIT2', 'Green_Vegetables_Consumption': 'FVGREEN1', 'FriedPotato_Consumption': 'FRENCHF1'}

def correct(s):
    v = pd.Series(np.nan, index=s.index)
    d = (s >= 101) & (s <= 199); w = (s >= 201) & (s <= 299); m = (s >= 301) & (s <= 399)
    v[d] = (s[d] - 100) * 30; v[w] = (s[w] - 200) * 4; v[m] = s[m] - 300; v[s == 300] = 0.5; v[s == 555] = 0
    return v

cols = list(Ff.columns)
C = b0.copy(); C['Sex'] = r._SEX.map({1: 'Male', 2: 'Female'})
for c, s in FC.items():
    C[c] = correct(r[s])
C = C[cols].dropna()
assert Ff.index.isin(C.index).all()
inF = C.index.isin(Ff.index)
y = (C.Heart_Disease == 'Yes').astype(int).values
X = C.drop(columns='Heart_Disease'); XF = Ff.drop(columns='Heart_Disease'); yF = (Ff.Heart_Disease == 'Yes').astype(int)
num = ['Height_(cm)', 'Weight_(kg)', 'BMI', 'Alcohol_Consumption'] + list(FC)
cat = [c for c in X.columns if c not in num]
print('C', len(C), 'F', int(inF.sum()), 'excluded', int((~inF).sum()))
print('Q4 prevalence: F', t4(yF.mean()), '| C', t4(y.mean()), '| excluded', t4(y[~inF].mean()))

def lr():
    return make_pipeline(ColumnTransformer([('n', StandardScaler(), num), ('c', OneHotEncoder(handle_unknown='ignore'), cat)]),
                         LogisticRegression(C=1.0, max_iter=2000))
def gbm(Xtr, ytr):
    Xc = Xtr.copy()
    for c in cat: Xc[c] = Xc[c].astype(pd.CategoricalDtype(sorted(X[c].unique())))
    m = lgb.LGBMClassifier(n_estimators=100, learning_rate=0.1, num_leaves=31, verbose=-1, n_jobs=2).fit(Xc, ytr)
    def pred(Xt):
        Xt = Xt.copy()
        for c in cat: Xt[c] = Xt[c].astype(pd.CategoricalDtype(sorted(X[c].unique())))
        return m.predict_proba(Xt)[:, 1]
    return pred
def fit(kind, Xtr, ytr):
    if kind == 'lr':
        m = lr().fit(Xtr, ytr); return lambda Xt: m.predict_proba(Xt)[:, 1]
    return gbm(Xtr, ytr)

def boot(yt, pa, pb, n=200, seed=0):
    rng = np.random.default_rng(seed); out = []
    for _ in range(n):
        i = rng.integers(0, len(yt), len(yt))
        if yt[i].min() == yt[i].max(): continue
        out.append(roc_auc_score(yt[i], pb[i]) - roc_auc_score(yt[i], pa[i]))
    return np.percentile(out, [2.5, 97.5])

idx = np.arange(len(C))
for kind in ['lr', 'gbm']:
    q1 = []; q2 = []; aucB = []; q2ex = []
    for seed in range(5):
        tr, te = train_test_split(idx, test_size=0.3, stratify=y, random_state=seed)
        trF = tr[inF[tr]]
        A = fit(kind, XF.loc[C.index[trF]], yF.loc[C.index[trF]].values)   # file coding, file rows
        B = fit(kind, X.iloc[tr], y[tr])                                  # correct coding, all rows
        pa = A(X.iloc[te]); pb = B(X.iloc[te]); yt = y[te]
        a_A = roc_auc_score(yt, pa); a_B = roc_auc_score(yt, pb); aucB.append(a_B)
        q1.append(a_B - a_A)
        teF = inF[te]
        a_Fonly = roc_auc_score(yt[teF], pb[teF]); a_ex = roc_auc_score(yt[~teF], pb[~teF])
        q2.append(a_B - a_Fonly); q2ex.append(a_ex)
        if seed == 0:
            ci1 = boot(yt, pa, pb)
            # Q2 paired bootstrap: all-test AUC minus F-only AUC under the same resample
            rng = np.random.default_rng(1); d2 = []
            for _ in range(200):
                i = rng.integers(0, len(yt), len(yt)); f = teF[i]
                d2.append(roc_auc_score(yt[i], pb[i]) - roc_auc_score(yt[i][f], pb[i][f]))
            ci2 = np.percentile(d2, [2.5, 97.5])
        print(kind, 'seed', seed, 'AUC A', t4(a_A), 'B', t4(a_B), 'B on F-only', t4(a_Fonly), 'B on excluded', t4(a_ex), time.strftime('%H:%M:%S'), flush=True)
    rngB = max(aucB) - min(aucB)
    for name, d, ci in [('Q1 B-A', q1, ci1), ('Q2 all-Fonly', q2, ci2)]:
        med = float(np.median(d))
        mat = abs(med) >= 0.01 and abs(med) > rngB and (ci[0] > 0 or ci[1] < 0)
        notm = abs(med) < 0.01 and ci[0] >= -0.01 and ci[1] <= 0.01
        print(kind, name, 'median', t4(med), 'range', t4(min(d)), t4(max(d)), 'ref range', t4(rngB), 'CI', t4(ci[0]), t4(ci[1]),
              'MATERIAL' if mat else ('not material' if notm else 'inconclusive'))
    print(kind, 'excluded-only AUC median', t4(float(np.median(q2ex))))

# Q3 adjusted odds ratios per 30 servings/month
def orfit(D, yy):
    out = {}
    base = pd.get_dummies(D[['Age_Category', 'Sex']], drop_first=True).astype(float)
    for c in FC:
        Z = sm.add_constant(pd.concat([D[c] / 30, base], axis=1))
        m = sm.Logit(yy, Z).fit(disp=0); b = m.params[c]; se = m.bse[c]
        out[c] = (np.exp(b), np.exp(b - 1.96 * se), np.exp(b + 1.96 * se))
    return out
oF = orfit(XF, yF.values); oC = orfit(X, y)
for c in FC:
    f, cc_ = oF[c], oC[c]
    overlap = not (f[2] < cc_[1] or cc_[2] < f[1]); opp = (f[0] - 1) * (cc_[0] - 1) < 0
    print('Q3', c, 'file OR', t4(f[0]), f'({t4(f[1])}-{t4(f[2])})', '| correct OR', t4(cc_[0]), f'({t4(cc_[1])}-{t4(cc_[2])})',
          'MATERIAL' if (not overlap or opp) else 'not material')
