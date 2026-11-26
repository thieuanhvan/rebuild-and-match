"""C. Independent rebuild of Kaggle heart_2022_with_nans from raw LLCP2022; DK counts; race."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import pandas as pd, numpy as np
V = WORK_ROOT + '/verify2'
wn = pd.read_csv(f'{V}/kaggle/heart_2022_with_nans.csv')
nn = pd.read_csv(f'{V}/kaggle/heart_2022_no_nans.csv')
raw = pd.read_parquet(f'{V}/raw/raw2022.parquet')
out = open(f'{V}/c_out.txt', 'w', encoding='utf-8')
def P(*a):
    print(*a); print(*a, file=out, flush=True)
def tr(x): return int(x * 10000) / 10000

P('with_nans rows', len(wn), 'no_nans rows', len(nn), 'raw rows', len(raw))
for c in wn.columns:
    v = wn[c].value_counts(dropna=False)
    P(' ', c, 'NaN', int(wn[c].isna().sum()), dict(v.head(9)) if len(v) < 25 else f'min {wn[c].min()} max {wn[c].max()}')

# --- mapping inferred from value sets ---
yn = {1: 'Yes', 2: 'No'}
src = {  # Kaggle column -> raw variable
 'Sex': 'SEXVAR', 'GeneralHealth': 'GENHLTH', 'PhysicalHealthDays': 'PHYSHLTH', 'MentalHealthDays': 'MENTHLTH',
 'LastCheckupTime': 'CHECKUP1', 'PhysicalActivities': 'EXERANY2', 'SleepHours': 'SLEPTIM1', 'RemovedTeeth': 'RMVTETH4',
 'HadHeartAttack': 'CVDINFR4', 'HadAngina': 'CVDCRHD4', 'HadStroke': 'CVDSTRK3', 'HadAsthma': 'ASTHMA3',
 'HadSkinCancer': 'CHCSCNC1', 'HadCOPD': 'CHCCOPD3', 'HadDepressiveDisorder': 'ADDEPEV3', 'HadKidneyDisease': 'CHCKDNY2',
 'HadArthritis': 'HAVARTH4', 'HadDiabetes': 'DIABETE4', 'DeafOrHardOfHearing': 'DEAF', 'BlindOrVisionDifficulty': 'BLIND',
 'DifficultyConcentrating': 'DECIDE', 'DifficultyWalking': 'DIFFWALK', 'DifficultyDressingBathing': 'DIFFDRES',
 'DifficultyErrands': 'DIFFALON', 'SmokerStatus': '_SMOKER3', 'ECigaretteUsage': 'ECIGNOW2', 'ChestScan': 'LCSCTSC1',
 'RaceEthnicityCategory': '_RACEGR4', 'AgeCategory': '_AGEG5YR', 'HeightInMeters': 'HTM4', 'WeightInKilograms': 'WTKG3',
 'BMI': '_BMI5', 'AlcoholDrinkers': 'DRNKANY6', 'HIVTesting': 'HIVTST7', 'FluVaxLast12': 'FLUSHOT7',
 'PneumoVaxEver': 'PNEUVAC4', 'TetanusLast10Tdap': 'TETANUS1', 'HighRiskLastYear': 'HIVRISK5', 'CovidPos': 'COVIDPOS'}

# Learn category labels by aligning row order (with_nans should follow raw order) -- check first
aligned = len(wn) == len(raw)
P('\nrow counts equal (raw vs with_nans):', aligned)
rec = pd.DataFrame(index=raw.index)
codemap = {}
for kc, rc in src.items():
    if kc in ('PhysicalHealthDays', 'MentalHealthDays', 'SleepHours', 'HeightInMeters', 'WeightInKilograms', 'BMI'):
        continue
    if aligned:
        ct = pd.crosstab(raw[rc].fillna(-1), wn[kc].fillna('<NaN>'))
        m = {}
        for code in ct.index:
            row = ct.loc[code]
            lab = row.idxmax(); m[code] = lab
            purity = row.max() / row.sum()
            if purity < 0.9999:
                P(f'  impure {kc}<-{rc} code {code}: {dict(row[row > 0])}')
        codemap[kc] = m
        P(f' map {kc}<-{rc}:', m)
rec_cat = {kc: raw[src[kc]].fillna(-1).map(m).replace('<NaN>', np.nan) for kc, m in codemap.items()}
rec = pd.DataFrame(rec_cat)
rec['State'] = np.nan
def days(s):
    return s.replace({88: 0}).where(s.between(1, 30) | (s == 88))
rec['PhysicalHealthDays'] = days(raw.PHYSHLTH)
rec['MentalHealthDays'] = days(raw.MENTHLTH)
rec['SleepHours'] = raw.SLEPTIM1.where(raw.SLEPTIM1.between(1, 24))
rec['HeightInMeters'] = raw.HTM4 / 100
rec['WeightInKilograms'] = raw.WTKG3 / 100
rec['BMI'] = raw._BMI5 / 100
# State: learn mapping from FIPS by alignment
st = pd.crosstab(raw._STATE, wn.State)
rec['State'] = raw._STATE.map(st.idxmax(axis=1))
P(' State mapping purity min:', (st.max(axis=1) / st.sum(axis=1)).min())
rec = rec[wn.columns]

# cell-level comparison for numeric columns (codes for categorical are learned, so the test there is purity + NaN agreement)
P('\nCell-level agreement, rebuilt vs with_nans (row-aligned):')
allok = True
for c in wn.columns:
    a, b = rec[c], wn[c]
    if a.dtype.kind == 'f' or b.dtype.kind == 'f':
        eq = (np.isclose(a.astype(float), b.astype(float), atol=0.006) | (a.isna() & b.isna()))
    else:
        eq = (a == b) | (a.isna() & b.isna())
    nbad = int((~eq).sum())
    if nbad:
        allok = False
        P(f'  {c}: {nbad} mismatching cells; NaN rebuilt {int(a.isna().sum())} vs file {int(b.isna().sum())}')
P(' all columns agree:', allok)

# no_nans == complete cases of with_nans?
cc = wn.dropna()
P('\nwith_nans complete cases', len(cc), 'no_nans', len(nn))
def ms(x, y):
    x = x.copy(); y = y.copy()
    for c in x.columns:
        if x[c].dtype.kind == 'f': x[c] = x[c].round(2); y[c] = y[c].round(2)
    ca, cb = x.value_counts(), y.value_counts()
    j = pd.concat([ca.rename('a'), cb.rename('b')], axis=1).fillna(0)
    return np.minimum(j.a, j.b).sum() / max(len(x), len(y))
P(' multiset match no_nans vs with_nans.dropna():', ms(cc.reset_index(drop=True), nn))

# DK counts on the raw source variables (non-derived, with 7/77 = don't know)
raw_src = [v for v in src.values() if not v.startswith('_') and v not in ('HTM4', 'WTKG3')]
dk = pd.Series(False, index=raw.index); dkr = pd.Series(False, index=raw.index)
for v in raw_src:
    if v in ('PHYSHLTH', 'MENTHLTH', 'SLEPTIM1'):
        dk |= raw[v] == 77; dkr |= raw[v].isin([77, 99])
    else:
        dk |= raw[v] == 7; dkr |= raw[v].isin([7, 9])
P('\nC. raw respondents with >=1 DK (7/77) on', len(raw_src), 'raw source vars:', int(dk.sum()))
P('   with >=1 DK or refused (7/9/77/99):', int(dkr.sum()))
# add derived vars' DK/refused/missing codes
dk_der = dk | (raw._SMOKER3 == 9) | (raw._RACEGR4 == 9) | (raw._AGEG5YR == 14)
P('   DK on raw vars OR derived 9/14 codes (_SMOKER3, _RACEGR4, _AGEG5YR):', int(dk_der.sum()))
# are DK cells NaN in with_nans?
dk_nan_ok = True
for kc, rc in src.items():
    if rc.startswith('_') or rc in ('HTM4', 'WTKG3'): continue
    code = 77 if rc in ('PHYSHLTH', 'MENTHLTH', 'SLEPTIM1') else 7
    m = raw[rc] == code
    nn_ = int(wn.loc[m, kc].notna().sum())
    if nn_:
        dk_nan_ok = False; P(f'  {kc}: {nn_} DK cells NOT NaN in with_nans')
P(' every DK cell is NaN in with_nans:', dk_nan_ok)
P(' DK respondents with a complete with_nans row (would be in no_nans):', int(wn.loc[dk].notna().all(axis=1).sum()))
P(' DK-or-refused respondents with a complete row:', int(wn.loc[dkr].notna().all(axis=1).sum()))

# race
P('\nRace: raw _RACEGR4 counts', dict(raw._RACEGR4.value_counts(dropna=False)))
P(' raw _RACEGR4 == 9 or NaN:', int((raw._RACEGR4 == 9).sum() + raw._RACEGR4.isna().sum()))
P(' with_nans RaceEthnicityCategory NaN:', int(wn.RaceEthnicityCategory.isna().sum()))
P(' crosstab _RACEGR4 vs NaN-race:', pd.crosstab(raw._RACEGR4.fillna(-1), wn.RaceEthnicityCategory.isna()).to_dict())
P(' raw _RACE1 == 9:', int((raw._RACE1 == 9).sum()), '; _IMPRACE counts', dict(raw._IMPRACE.value_counts(dropna=False)))
rn = wn.RaceEthnicityCategory.isna()
P(' rows with NaN race: _RACE1 counts', dict(raw.loc[rn, '_RACE1'].value_counts(dropna=False)), '_HISPANC', dict(raw.loc[rn, '_HISPANC'].value_counts(dropna=False)))
r9 = raw._RACEGR4 == 9
P(' rows with _RACEGR4==9 but race not NaN in file:', dict(wn.loc[r9 & ~rn, 'RaceEthnicityCategory'].value_counts()))
P(' rows with race NaN but _RACEGR4 != 9:', dict(raw.loc[rn & ~r9, '_RACEGR4'].value_counts(dropna=False)))
# Other race only in no_nans via linking: complete-case rows of with_nans
cc_idx = wn.dropna().index
oth = wn.loc[cc_idx, 'RaceEthnicityCategory'] == 'Other race only, Non-Hispanic'
P('\n no_nans (via with_nans complete cases) Other race only NH:', int(oth.sum()), '; no_nans file count:', int((nn.RaceEthnicityCategory == 'Other race only, Non-Hispanic').sum()))
P(' _RACE1 among them (3=AIAN,4=Asian,5=NHPI,6=Other race only):', dict(raw.loc[cc_idx[oth.values], '_RACE1'].value_counts(dropna=False)))
P(' _MRACE2 among them:', dict(raw.loc[cc_idx[oth.values], '_MRACE2'].value_counts(dropna=False)))
out.close()
