"""Read needed columns from raw BRFSS XPT in chunks; save parquet in verify2/raw/."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import pandas as pd, sys, time
V = WORK_ROOT + '/verify2'
files = {2015: SURVEY_DATA_ROOT + '/brfss/2015/xpt_unzipped/LLCP2015.XPT',
         2020: V + '/raw/LLCP2020.XPT', 2022: V + '/raw/LLCP2022.XPT'}
cols = {
 2015: 'SEQNO _STATE DIABETE3 _RFHYPE5 TOLDHI2 _CHOLCHK _BMI5 SMOKE100 CVDSTRK3 _MICHD CVDINFR4 CVDCRHD4 _TOTINDA _FRTLT1 _VEGLT1 _RFDRHV5 HLTHPLN1 MEDCOST GENHLTH MENTHLTH PHYSHLTH DIFFWALK SEX _AGEG5YR EDUCA INCOME2 BPHIGH4 PREDIAB1'.split(),
 2020: 'SEQNO _STATE _MICHD CVDINFR4 CVDCRHD4 _BMI5 SMOKE100 _RFDRHV7 CVDSTRK3 PHYSHLTH MENTHLTH DIFFWALK SEXVAR _SEX _AGEG5YR _RACE _IMPRACE _RACEGR3 _RACEG21 _MRACE1 _HISPANC _PRACE1 DIABETE4 EXERANY2 _TOTINDA GENHLTH SLEPTIM1 ASTHMA3 CHCKDNY2 CHCSCNCR'.split(),
 2022: 'SEQNO _STATE SEXVAR GENHLTH PHYSHLTH MENTHLTH CHECKUP1 EXERANY2 SLEPTIM1 RMVTETH4 CVDINFR4 CVDCRHD4 CVDSTRK3 ASTHMA3 CHCSCNC1 CHCCOPD3 ADDEPEV3 CHCKDNY2 HAVARTH4 DIABETE4 DEAF BLIND DECIDE DIFFWALK DIFFDRES DIFFALON _SMOKER3 ECIGNOW2 LCSCTSC1 _RACEGR4 _RACE1 _IMPRACE _MRACE2 _PRACE2 _HISPANC _RACEG22 _RACEPR1 _AGEG5YR HTM4 WTKG3 _BMI5 DRNKANY6 HIVTST7 FLUSHOT7 PNEUVAC4 TETANUS1 HIVRISK5 COVIDPOS _MICHD SMOKE100 SMOKDAY2 ECIGNOW2 ALCDAY4 HEIGHT3 WEIGHT2'.split(),
}
for y in [int(a) for a in sys.argv[1:]] or [2015, 2020, 2022]:
    t = time.time(); parts = []
    want = list(dict.fromkeys(cols[y]))
    for ch in pd.read_sas(files[y], format='xport', chunksize=50000):
        keep = [c for c in want if c in ch.columns]
        parts.append(ch[keep].copy())
    df = pd.concat(parts, ignore_index=True)
    if df['SEQNO'].dtype == object:
        df['SEQNO'] = df['SEQNO'].str.decode('ascii') if isinstance(df['SEQNO'].iloc[0], bytes) else df['SEQNO']
    df.to_parquet(f'{V}/raw/raw{y}.parquet')
    print(y, df.shape, 'missing cols:', [c for c in want if c not in df.columns], round(time.time() - t), 's', flush=True)
