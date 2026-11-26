"""C follow-up: per-variable DK counts and union variants to locate the 89,232 definition."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import pandas as pd, numpy as np
V = WORK_ROOT + '/verify2'
raw = pd.read_parquet(f'{V}/raw/raw2022.parquet')
wn = pd.read_csv(f'{V}/kaggle/heart_2022_with_nans.csv')
out = open(f'{V}/c2_out.txt', 'w', encoding='utf-8')
def P(*a):
    print(*a); print(*a, file=out, flush=True)
src = ['GENHLTH', 'PHYSHLTH', 'MENTHLTH', 'CHECKUP1', 'EXERANY2', 'SLEPTIM1', 'RMVTETH4', 'CVDINFR4', 'CVDCRHD4', 'CVDSTRK3',
       'ASTHMA3', 'CHCSCNC1', 'CHCCOPD3', 'ADDEPEV3', 'CHCKDNY2', 'HAVARTH4', 'DIABETE4', 'DEAF', 'BLIND', 'DECIDE', 'DIFFWALK',
       'DIFFDRES', 'DIFFALON', 'ECIGNOW2', 'LCSCTSC1', 'DRNKANY6', 'HIVTST7', 'FLUSHOT7', 'PNEUVAC4', 'TETANUS1', 'HIVRISK5', 'COVIDPOS']
num = {'PHYSHLTH', 'MENTHLTH', 'SLEPTIM1'}
dkm = pd.DataFrame({v: raw[v] == (77 if v in num else 7) for v in src})
rfm = pd.DataFrame({v: raw[v] == (99 if v in num else 9) for v in src})
P('per-variable DK counts:', dict(dkm.sum().sort_values(ascending=False)))
anydk = dkm.any(axis=1)
P('any DK, all', len(src), 'vars:', int(anydk.sum()))
P('any DK excluding day/hour vars:', int(dkm.drop(columns=list(num)).any(axis=1).sum()))
P('any DK excluding CHECKUP1 7 (+8 never is not DK):', int(dkm.drop(columns=['CHECKUP1']).any(axis=1).sum()))
incomplete = wn.isna().any(axis=1)
k2r = {'GeneralHealth':'GENHLTH','PhysicalHealthDays':'PHYSHLTH','MentalHealthDays':'MENTHLTH','LastCheckupTime':'CHECKUP1','PhysicalActivities':'EXERANY2','SleepHours':'SLEPTIM1','RemovedTeeth':'RMVTETH4','HadHeartAttack':'CVDINFR4','HadAngina':'CVDCRHD4','HadStroke':'CVDSTRK3','HadAsthma':'ASTHMA3','HadSkinCancer':'CHCSCNC1','HadCOPD':'CHCCOPD3','HadDepressiveDisorder':'ADDEPEV3','HadKidneyDisease':'CHCKDNY2','HadArthritis':'HAVARTH4','HadDiabetes':'DIABETE4','DeafOrHardOfHearing':'DEAF','BlindOrVisionDifficulty':'BLIND','DifficultyConcentrating':'DECIDE','DifficultyWalking':'DIFFWALK','DifficultyDressingBathing':'DIFFDRES','DifficultyErrands':'DIFFALON','ECigaretteUsage':'ECIGNOW2','ChestScan':'LCSCTSC1','AlcoholDrinkers':'DRNKANY6','HIVTesting':'HIVTST7','FluVaxLast12':'FLUSHOT7','PneumoVaxEver':'PNEUVAC4','TetanusLast10Tdap':'TETANUS1','HighRiskLastYear':'HIVRISK5','CovidPos':'COVIDPOS'}
dkk = pd.DataFrame({k: dkm[r].values for k, r in k2r.items()}, index=wn.index).reindex(columns=wn.columns, fill_value=False)
nan_wo_dk = wn.isna() & ~dkk
P('rows with >=1 NaN not explained by DK:', int(nan_wo_dk.any(axis=1).sum()))
P('rows with >=1 DK AND >=1 other NaN:', int((anydk & nan_wo_dk.any(axis=1)).sum()))
P('rows excluded from no_nans:', int(incomplete.sum()))
only_dk = anydk & ~nan_wo_dk.any(axis=1)
P('rows whose ONLY NaNs come from DK codes:', int(only_dk.sum()))
# DK rows that would otherwise be complete
P('DK rows where every other column is observed (excluding DK cells):', int(only_dk.sum()))
# drop-one-variable variants to see if any match 89,232
for v in src:
    n = int(dkm.drop(columns=[v]).any(axis=1).sum())
    if abs(n - 89232) < 3000: P(' drop', v, n)
# cumulative unions in descending order of DK count
acc = pd.Series(False, index=raw.index)
for v in dkm.sum().sort_values().index:
    acc |= dkm[v]
    if abs(int(acc.sum()) - 89232) < 1500: P(' union of smallest-DK vars up to', v, int(acc.sum()))
# DK among respondents in the 246,022 complete-case universe? (by definition 0) - also among rows with complete data on the 2020-style subset
out.close()
