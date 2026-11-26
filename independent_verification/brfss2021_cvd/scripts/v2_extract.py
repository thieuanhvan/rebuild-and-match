import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import psutil,os; psutil.Process(os.getpid()).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
import pandas as pd
P=SURVEY_DATA_ROOT + r'/brfss/2021/xpt_unzipped/LLCP2021.XPT'
cols=['GENHLTH','CHECKUP1','EXERANY2','_MICHD','CHCSCNCR','CHCOCNCR','ADDEPEV3','DIABETE4','HAVARTH5','_SEX','_AGEG5YR','HTM4','WTKG3','_BMI5','SMOKE100','ALCDAY5','FRUIT2','FVGREEN1','FRENCHF1','PHYSHLTH','MENTHLTH']
parts=[]
for ch in pd.read_sas(P,format='xport',chunksize=50000):
    miss=[c for c in cols if c not in ch.columns]
    if miss: raise SystemExit(miss)
    parts.append(ch[cols].copy())
d=pd.concat(parts,ignore_index=True)
print(d.shape)
d.to_pickle('v2_raw.pkl')
