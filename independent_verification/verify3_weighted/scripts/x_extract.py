"""verify3: unzip 2020/2022 XPT + Kaggle heart CSVs into verify3/raw; save column subsets (incl. design vars) as parquet."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import zipfile, os, shutil, time
import pandas as pd
B = SURVEY_DATA_ROOT
V3 = WORK_ROOT + '/verify3'
R = V3 + '/raw'
for y in (2020, 2022):
    with zipfile.ZipFile(f'{B}/brfss/{y}/LLCP{y}XPT.zip') as z:
        for m in z.infolist():
            out = f'{R}/{os.path.basename(m.filename.strip())}'
            with z.open(m) as s, open(out, 'wb') as d:
                shutil.copyfileobj(s, d, 1 << 20)
            print(y, repr(m.filename), os.path.getsize(out), flush=True)
with zipfile.ZipFile(f'{B}/kaggle-heart-pytlak/heart_pytlak_archive.zip') as z:
    for m in z.infolist():
        if m.is_dir():
            continue
        out = f'{R}/{os.path.basename(m.filename)}'
        with z.open(m) as s, open(out, 'wb') as d:
            shutil.copyfileobj(s, d, 1 << 20)
        print(repr(m.filename), os.path.getsize(out), flush=True)

design = ['_LLCPWT', '_STSTR', '_PSU']
files = {2015: f'{B}/brfss/2015/xpt_unzipped/LLCP2015.XPT', 2020: f'{R}/LLCP2020.XPT', 2022: f'{R}/LLCP2022.XPT'}
cols = {
 2015: 'DIABETE3 _RFHYPE5 TOLDHI2 _CHOLCHK _BMI5 SMOKE100 CVDSTRK3 _MICHD _TOTINDA _FRTLT1 _VEGLT1 _RFDRHV5 HLTHPLN1 MEDCOST GENHLTH MENTHLTH PHYSHLTH DIFFWALK SEX _AGEG5YR EDUCA INCOME2'.split(),
 2020: '_MICHD CVDINFR4 CVDCRHD4 _BMI5 SMOKE100 _RFDRHV7 CVDSTRK3 PHYSHLTH MENTHLTH DIFFWALK SEXVAR _AGEG5YR _RACE _IMPRACE DIABETE4 EXERANY2 GENHLTH SLEPTIM1 ASTHMA3 CHCKDNY2 CHCSCNCR'.split(),
 2022: 'CVDINFR4 CVDCRHD4 _MICHD'.split(),
}
for y in (2015, 2020, 2022):
    t = time.time(); parts = []
    want = cols[y] + design
    for ch in pd.read_sas(files[y], format='xport', chunksize=50000):
        parts.append(ch[want].copy())
    df = pd.concat(parts, ignore_index=True)
    df.to_parquet(f'{R}/raw{y}.parquet')
    print(y, df.shape, round(time.time() - t), 's', flush=True)
