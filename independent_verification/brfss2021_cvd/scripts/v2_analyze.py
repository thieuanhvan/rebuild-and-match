import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import psutil,os; psutil.Process(os.getpid()).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
import pandas as pd, numpy as np, zipfile, math
def t4(x): return math.trunc(x*10000)/10000
d=pd.read_pickle('v2_raw.pkl')
print('raw rows',len(d))
z=zipfile.ZipFile(SURVEY_DATA_ROOT + r'/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip')
k=pd.read_csv(z.open('CVD_cleaned.csv')); print('kaggle rows',len(k))
def seq(x):
    x=x.copy()
    x[x.isin([300,777,999])]=np.nan
    m=(x>=101)&(x<=199); x[m]=(x[m]-100)*30
    m=(x>=201)&(x<=299); x[m]=(x[m]-200)*4
    m=(x>=300)&(x<=399); x[m]=x[m]-300
    x[x==555]=0
    return x
def correct(x):
    y=pd.Series(np.nan,index=x.index)
    m=(x>=101)&(x<=199); y[m]=(x[m]-100)*30
    m=(x>=201)&(x<=299); y[m]=(x[m]-200)*4
    y[x==300]=0.5
    m=(x>=301)&(x<=399); y[m]=x[m]-300
    y[x==555]=0
    return y
ex=pd.Series([107.,110.,299.]); print('examples',seq(ex).tolist())
yn=lambda s: s.map({1:'Yes',2:'No'})
o=pd.DataFrame(index=d.index)
o['General_Health']=d.GENHLTH.map({1:'Excellent',2:'Very Good',3:'Good',4:'Fair',5:'Poor'})
o['Checkup']=d.CHECKUP1.map({1:'Within the past year',2:'Within the past 2 years',3:'Within the past 5 years',4:'5 or more years ago',8:'Never'})
o['Exercise']=yn(d.EXERANY2); o['Heart_Disease']=yn(d._MICHD); o['Skin_Cancer']=yn(d.CHCSCNCR)
o['Other_Cancer']=yn(d.CHCOCNCR); o['Depression']=yn(d.ADDEPEV3)
o['Diabetes']=d.DIABETE4.map({1:'Yes',2:'Yes, but female told only during pregnancy',3:'No',4:'No, pre-diabetes or borderline diabetes'})
o['Arthritis']=yn(d.HAVARTH5); o['Sex']=d._SEX.map({1:'Male',2:'Female'})
ages=['18-24','25-29','30-34','35-39','40-44','45-49','50-54','55-59','60-64','65-69','70-74','75-79','80+']
o['Age_Category']=d._AGEG5YR.map({i+1:a for i,a in enumerate(ages)})
o['Height_(cm)']=d.HTM4; o['Weight_(kg)']=d.WTKG3/100; o['BMI']=d._BMI5/100
o['Smoking_History']=yn(d.SMOKE100)
a=d.ALCDAY5; al=pd.Series(np.nan,index=a.index)
m=(a>=101)&(a<=199); al[m]=(a[m]-100)*4
m=(a>=201)&(a<=299); al[m]=a[m]-200
al[a==888]=0; o['Alcohol_Consumption']=al
fc={'Fruit_Consumption':'FRUIT2','Green_Vegetables_Consumption':'FVGREEN1','FriedPotato_Consumption':'FRENCHF1'}
base=o.copy()
for c,r in fc.items(): o[c]=seq(d[r])
o=o[k.columns]
ph=d.PHYSHLTH; mh=d.MENTHLTH
phok=~(ph.isin([77,99])|ph.isna()|mh.isin([77,99])|mh.isna())
cap=(o[list(fc)]>128).any(axis=1)
kept=o[(~cap)&phok].dropna()
print('rebuilt rows',len(kept))
def keyed(df):
    df=df.copy()
    for c in df.columns:
        if df[c].dtype!=object: df[c]=df[c].astype(float).round(2)
    return df.astype(str).apply(lambda r:'|'.join(r),axis=1).value_counts()
A=keyed(kept); B=keyed(k)
diff=A.sub(B,fill_value=0)
print('rows only in rebuild',int(diff[diff>0].sum()),'only in kaggle',int(-diff[diff<0].sum()))
print('multiset equal',bool((diff==0).all()))
# claim 2 distributions
for c,r in fc.items():
    vr=kept[c].value_counts().sort_index(); vk=k[c].value_counts().sort_index()
    eq=vr.equals(vk) if len(vr)==len(vk) else False
    vk2=k[c].round(2).value_counts().sort_index(); vr2=kept[c].round(2).value_counts().sort_index()
    print(c,'dist equal',vr2.to_dict()==vk2.to_dict(),'n40',int((k[c]==40).sum()),'n210',int((k[c]==210).sum()),'max',k[c].max(),'n>128',int((k[c]>128).sum()),'nunique',k[c].nunique())
# claim 4
oc=base.copy()
for c,r in fc.items(): oc[c]=correct(d[r])
oc=oc[k.columns]
comp=oc.notna().all(axis=1)
print('complete under correct coding',int(comp.sum()))
raw=d[list(fc.values())]
has300=(raw==300).any(axis=1)
capc=cap
C=comp
print('nonexclusive: code300',int((C&has300).sum()),'cap',int((C&capc).sum()),'phys/ment',int((C&~phok).sum()))
r1=C&has300; r2=C&~has300&capc; r3=C&~has300&~capc&~phok
print('sequential: code300',int(r1.sum()),'cap',int(r2.sum()),'phys/ment',int(r3.sum()))
keptmask=C&~has300&~capc&phok
removed=C&~keptmask
print('kept',int(keptmask.sum()),'removed',int(removed.sum()))
hd=oc.Heart_Disease=='Yes'
print('HD share removed',t4(hd[removed].mean()),'HD share file',t4((k.Heart_Disease=='Yes').mean()),'HD kept',t4(hd[keptmask].mean()))
wrong=(oc.loc[keptmask,list(fc)].values!=o.loc[keptmask,list(fc)].values).any(axis=1)
print('kept rows with >=1 wrong consumption value',int(wrong.sum()))
for c in fc: print(' ',c,int((oc.loc[keptmask,c]!=o.loc[keptmask,c]).sum()))
