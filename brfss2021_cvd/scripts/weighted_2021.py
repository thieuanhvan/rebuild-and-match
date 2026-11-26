"""I360: weighted _MICHD prevalence (design-based SE, Taylor linearization, PSU with replacement within strata, singleton strata contribute 0)
among all valid respondents and in the file population; file duplicates; flow counts."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import hashlib, numpy as np, pandas as pd
W=WORK_ROOT + '/brfss2021_cvd/'
r=pd.read_pickle(W+'raw2021_sub.pkl'); F=pd.read_pickle(W+'rebuild_exact_cc.pkl')
t4=lambda x:int(x*10000)/10000
def wprev(mask):
    d=r[mask]; y=(d._MICHD==1).astype(float); w=d._LLCPWT; p=(w*y).sum()/w.sum()
    z=w*(y-p)/w.sum(); g=pd.DataFrame({'s':d._STSTR,'u':d._PSU,'z':z}).groupby(['s','u']).z.sum().reset_index()
    v=0; single=0
    for s,gg in g.groupby('s'):
        n=len(gg)
        if n<2: single+=1; continue
        v+=n/(n-1)*((gg.z-gg.z.mean())**2).sum()
    return p,np.sqrt(v),single
valid=r._MICHD.isin([1,2])
for lab,m in [('all valid',valid),('file population',r.index.isin(F.index))]:
    p,se,s=wprev(m); print(lab,'n',int(m.sum()),'weighted',t4(p),'SE',t4(se),'singleton strata',s)
print('file unweighted',t4((F.Heart_Disease=='Yes').mean()),'positives',int((F.Heart_Disease=='Yes').sum()))
print('valid _MICHD',int(valid.sum()))
print('dup rows beyond first',int(F.duplicated().sum()))
h=hashlib.sha256(open(SURVEY_DATA_ROOT + '/brfss/2021/LLCP2021XPT.zip','rb').read()).hexdigest(); print('zip sha256',h)
