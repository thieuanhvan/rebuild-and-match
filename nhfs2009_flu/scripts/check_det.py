import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import runpy, sys, io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a4_k1.py'))
T, SPLITS = g['T'], g['SPLITS']
from sklearn.metrics import roc_auc_score
i, j = SPLITS[0]; a, b = T.iloc[i], T.iloc[j]
for rep in range(3):
    A, B = g['lr_pair'](g['num'], g['cat'])(a, b)
    p = g['predict']('lr', A, a.h1n1_vaccine.values, B)
    print('rep', rep, roc_auc_score(b.h1n1_vaccine.values, p), A.shape)
nb = g['num_b']
A, B = g['lr_pair'](nb, g['cat'])(a, b)
p = g['predict']('lr', A, a.h1n1_vaccine.values, B)
print('Q3 B split0', roc_auc_score(b.h1n1_vaccine.values, p), A.shape)
from sklearn.metrics import roc_auc_score as r
import numpy as np
for s,(i2,j2) in enumerate(SPLITS):
    a2,b2=T.iloc[i2],T.iloc[j2]
    A1,B1=g['lr_pair'](g['num'],g['cat'])(a2,b2); A2,B2=g['lr_pair'](nb,g['cat'])(a2,b2)
    pa=g['predict']('lr',A1,a2.h1n1_vaccine.values,B1); pb=g['predict']('lr',A2,a2.h1n1_vaccine.values,B2)
    print(s, r(b2.h1n1_vaccine,pa), r(b2.h1n1_vaccine,pb))
