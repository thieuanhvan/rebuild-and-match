import math
def trunc(x): return math.floor(x*10000)/10000
def kappa(a,b):
    n=len(a); cats=set(a)|set(b); po=sum(x==y for x,y in zip(a,b))/n
    pe=sum((a.count(c)/n)*(b.count(c)/n) for c in cats)
    return po, (None if pe==1 else (po-pe)/(1-pe))
c2  = ['Y' if i in (3,18,23) else 'N' for i in range(1,24)]
c1  = ['Y' if i in (3,18,23) else 'N' for i in range(1,24)]  # listed MISDESCRIBES = Y, else not listed
for name,(a,b) in {'all23_misdesc':(c1,c2),'Q3_both_Q2yes_strict_n3':(['Y']*3,['Y']*3),'Q3_incl_C09_n4':(['Y','Y','Y','N'],['Y','Y','Y','N'])}.items():
    po,k=kappa(a,b); print(name,'n',len(a),'agree',sum(x==y for x,y in zip(a,b)),'po',trunc(po),'kappa',None if k is None else trunc(k))
