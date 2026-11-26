"""Step 0 for the 2021 file: read the BRFSS 2021 XPT file and save the columns the rebuild scripts use.
Writes WORK_ROOT/raw2021_sub.pkl (28 columns) and WORK_ROOT/raw2021_physment.pkl (PHYSHLTH, MENTHLTH).
Usage: python -I -X utf8 extract_raw2021.py
Input: SURVEY_DATA_ROOT/brfss/2021/LLCP2021.XPT (CDC annual data page, 2021)."""
import os
import pandas as pd

DATA = os.environ.get('SURVEY_DATA_ROOT', 'path/to/survey_data')
WORK = os.path.join(os.environ.get('WORK_ROOT', 'path/to/work'), 'brfss2021_cvd')
SUB = ['FRUIT2', 'FRUITJU2', 'FVGREEN1', 'FRENCHF1', 'POTATOE1', 'VEGETAB2', 'ALCDAY5', 'HTM4', 'WTKG3', '_BMI5',
       'SMOKE100', '_AGEG5YR', 'SEXVAR', '_SEX', 'CHECKUP1', 'EXERANY2', '_MICHD', 'CVDINFR4', 'CVDCRHD4', 'CHCSCNCR',
       'CHCOCNCR', 'ADDEPEV3', 'DIABETE4', 'HAVARTH5', 'GENHLTH', '_LLCPWT', '_STSTR', '_PSU']
raw = pd.read_sas(os.path.join(DATA, 'brfss', '2021', 'LLCP2021.XPT'), format='xport')
os.makedirs(WORK, exist_ok=True)
raw[SUB].astype('float64').to_pickle(os.path.join(WORK, 'raw2021_sub.pkl'))
raw[['PHYSHLTH', 'MENTHLTH']].astype('float64').to_pickle(os.path.join(WORK, 'raw2021_physment.pkl'))
print('rows', len(raw))
