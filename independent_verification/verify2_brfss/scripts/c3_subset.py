"""C follow-up after comparison: union of DK on PNEUVAC4/TETANUS1/LCSCTSC1/HIVTST7/COVIDPOS + CHECKUP1 never (8)."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import pandas as pd
V = WORK_ROOT + '/verify2'
raw = pd.read_parquet(f'{V}/raw/raw2022.parquet')
wn = pd.read_csv(f'{V}/kaggle/heart_2022_with_nans.csv')
m = (raw.PNEUVAC4 == 7) | (raw.TETANUS1 == 7) | (raw.LCSCTSC1 == 7) | (raw.HIVTST7 == 7) | (raw.COVIDPOS == 7) | (raw.CHECKUP1 == 8)
cc = wn.notna().all(axis=1)
with open(f'{V}/c3_out.txt', 'w', encoding='utf-8') as f:
    for line in [f'CHECKUP1==8 (never): {int((raw.CHECKUP1 == 8).sum())}; CHECKUP1==7 (DK): {int((raw.CHECKUP1 == 7).sum())}',
                 f'union 5 DK vars + CHECKUP1 never: {int(m.sum())}; of them complete in with_nans (=in no_nans): {int((m & cc).sum())}',
                 f'union 5 DK vars only: {int(((raw.PNEUVAC4 == 7) | (raw.TETANUS1 == 7) | (raw.LCSCTSC1 == 7) | (raw.HIVTST7 == 7) | (raw.COVIDPOS == 7)).sum())}']:
        print(line); f.write(line + '\n')
