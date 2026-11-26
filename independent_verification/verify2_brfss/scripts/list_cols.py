import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import pandas as pd, sys
V = WORK_ROOT + '/verify2'
files = {2015: SURVEY_DATA_ROOT + '/brfss/2015/xpt_unzipped/LLCP2015.XPT',
         2020: V + '/raw/LLCP2020.XPT', 2022: V + '/raw/LLCP2022.XPT'}
try:
    import pyarrow; print('pyarrow', pyarrow.__version__)
except Exception as e:
    print('no pyarrow', e)
for y, f in files.items():
    r = pd.read_sas(f, format='xport', chunksize=10)
    c = next(r)
    print(y, len(c.columns))
    print(' '.join(c.columns))
    r.close()
