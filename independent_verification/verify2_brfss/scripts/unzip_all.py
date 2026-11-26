"""Extract BRFSS 2020/2022 XPT and Kaggle heart CSVs into verify2/raw and verify2/kaggle."""
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import zipfile, os, shutil
B = SURVEY_DATA_ROOT
V = WORK_ROOT + '/verify2'
for y in (2020, 2022):
    with zipfile.ZipFile(f'{B}/brfss/{y}/LLCP{y}XPT.zip') as z:
        for m in z.infolist():
            out = f'{V}/raw/{os.path.basename(m.filename.strip())}'
            with z.open(m) as src, open(out, 'wb') as dst:
                shutil.copyfileobj(src, dst, 1 << 20)
            print(y, repr(m.filename), '->', out, os.path.getsize(out))
with zipfile.ZipFile(f'{B}/kaggle-heart-pytlak/heart_pytlak_archive.zip') as z:
    for m in z.infolist():
        if m.is_dir():
            continue
        out = f'{V}/kaggle/{os.path.basename(m.filename)}'
        with z.open(m) as src, open(out, 'wb') as dst:
            shutil.copyfileobj(src, dst, 1 << 20)
        print(repr(m.filename), '->', out, os.path.getsize(out))
