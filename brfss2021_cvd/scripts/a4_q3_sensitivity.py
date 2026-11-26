"""I360 Q3 sensitivity (post hoc, labelled as such): separate the recode bug from row selection and from outliers."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import numpy as np, pandas as pd, statsmodels.api as sm
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a4_i360.py'), encoding='utf8').read()
exec(src.split('idx = np.arange')[0])
t = lambda x: int(x*10000)/10000
def orr(D, yy, c):
    base = pd.get_dummies(D[['Age_Category', 'Sex']], drop_first=True).astype(float)
    Z = sm.add_constant(pd.concat([D[c] / 30, base], axis=1)); m = sm.Logit(yy, Z).fit(disp=0)
    b, se = m.params[c], m.bse[c]; return f'{t(np.exp(b))} ({t(np.exp(b-1.96*se))}-{t(np.exp(b+1.96*se))})'
XcF = X.loc[XF.index]; ycF = y[inF]
for c in FC:
    capC = (X[list(FC)] <= 128).all(axis=1).values
    print(c, '| file rows, file coding', orr(XF, yF.values, c), '| file rows, correct coding', orr(XcF, ycF, c),
          '| C, correct, all values <=128', orr(X[capC], y[capC], c), '| C correct', orr(X, y, c))
