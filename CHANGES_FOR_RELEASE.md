# Changes made for the public release

Only the copies in this folder were changed; the original working files were not modified. Analysis logic is unchanged.

## Common change in every script listed below

Three lines were added after the module docstring (or at the top when there is none):

```python
import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
```

Hard-coded absolute paths were then replaced: raw and published data paths now start from `SURVEY_DATA_ROOT` (same sub-folder names as the README layout; the local Kaggle diabetes 2015 folder became `SURVEY_DATA_ROOT/kaggle-diabetes-2015`); working and output folders now start from `WORK_ROOT`; `sys.path` entries, `open()` and `runpy.run_path()` calls that pointed at the script's own folder now use `os.path.dirname(os.path.abspath(__file__))`. Local paths are shown below as placeholders.

## Scripts changed (old line -> new line)

### `brfss2015_diabetes/scripts/verify_independent_i336.py`

```diff
-K = "<local Kaggle diabetes 2015 folder>/"
-UCI = "<local data folder>/brfss/uci-891/data.csv"
-XPT = "<local data folder>/brfss/2015/xpt_unzipped/LLCP2015.XPT"
+K = SURVEY_DATA_ROOT + "/kaggle-diabetes-2015/"
+UCI = SURVEY_DATA_ROOT + "/brfss/uci-891/data.csv"
+XPT = SURVEY_DATA_ROOT + "/brfss/2015/xpt_unzipped/LLCP2015.XPT"
```

### `brfss2015_diabetes/scripts/q1_diabetes.py`

```diff
-C = '<local project folder>'
-F = '<local Kaggle diabetes 2015 folder>/diabetes_012_health_indicators_BRFSS2015.csv'
+C = WORK_ROOT + '/consequence'
+F = SURVEY_DATA_ROOT + '/kaggle-diabetes-2015/diabetes_012_health_indicators_BRFSS2015.csv'
```

### `brfss2020_2022_heart/scripts/q2q3_heart.py`

```diff
-BASE = '<local project folder>'
+BASE = WORK_ROOT + '/consequence'
```

### `brfss2021_cvd/scripts/rebuild_cvd2021_v1.py`

```diff
-W = '<local project folder>'
-K = '<local data folder>/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip'
+W = WORK_ROOT + '/brfss2021_cvd/'
+K = SURVEY_DATA_ROOT + '/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip'
```

### `brfss2021_cvd/scripts/rebuild_cvd2021_search.py`

```diff
-W = '<local project folder>'
-K = '<local data folder>/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip'
+W = WORK_ROOT + '/brfss2021_cvd/'
+K = SURVEY_DATA_ROOT + '/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip'
```

### `brfss2021_cvd/scripts/rebuild_cvd2021_sequential.py`

```diff
-W = '<local project folder>'
-K = '<local data folder>/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip'
+W = WORK_ROOT + '/brfss2021_cvd/'
+K = SURVEY_DATA_ROOT + '/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip'
```

### `brfss2021_cvd/scripts/find_extra_rule.py`

```diff
-W = '<local project folder>'
-K = '<local data folder>/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip'
-XPT = '<local data folder>/brfss/2021/xpt_unzipped/LLCP2021.XPT'
+W = WORK_ROOT + '/brfss2021_cvd/'
+K = SURVEY_DATA_ROOT + '/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip'
+XPT = SURVEY_DATA_ROOT + '/brfss/2021/xpt_unzipped/LLCP2021.XPT'
```

### `brfss2021_cvd/scripts/find_extra_rule2.py`

```diff
-W = '<local project folder>'
-K = '<local data folder>/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip'
-XPT = '<local data folder>/brfss/2021/xpt_unzipped/LLCP2021.XPT'
+W = WORK_ROOT + '/brfss2021_cvd/'
+K = SURVEY_DATA_ROOT + '/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip'
+XPT = SURVEY_DATA_ROOT + '/brfss/2021/xpt_unzipped/LLCP2021.XPT'
```

### `brfss2021_cvd/scripts/rebuild_cvd2021_final.py`

```diff
-W = '<local project folder>'
-K = '<local data folder>/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip'
+W = WORK_ROOT + '/brfss2021_cvd/'
+K = SURVEY_DATA_ROOT + '/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip'
```

### `brfss2021_cvd/scripts/a4_i360.py`

```diff
-W = '<local project folder>'
+W = WORK_ROOT + '/brfss2021_cvd/'
```

### `brfss2021_cvd/scripts/a4_q3_sensitivity.py`

```diff
-src = open('<local project folder>', encoding='utf8').read()
+src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a4_i360.py'), encoding='utf8').read()
```

### `brfss2021_cvd/scripts/weighted_2021.py`

```diff
-W='<local project folder>'
+W=WORK_ROOT + '/brfss2021_cvd/'
-h=hashlib.sha256(open('<local data folder>/brfss/2021/LLCP2021XPT.zip','rb').read()).hexdigest(); print('zip sha256',h)
+h=hashlib.sha256(open(SURVEY_DATA_ROOT + '/brfss/2021/LLCP2021XPT.zip','rb').read()).hexdigest(); print('zip sha256',h)
```

### `nhfs2009_flu/scripts/read_nhfs.py`

```diff
-R = '<local data folder>/nhfs-2009/raw/'
-W = '<local project folder>'
+R = SURVEY_DATA_ROOT + '/nhfs-2009/raw/'
+W = WORK_ROOT + '/nhfs2009_flu/'
```

### `nhfs2009_flu/scripts/rebuild_k1.py`

```diff
-W = '<local project folder>'
-K = '<local data folder>/flushot-kaggle/raw/'
+W = WORK_ROOT + '/nhfs2009_flu/'
+K = SURVEY_DATA_ROOT + '/flushot-kaggle/raw/'
```

### `nhfs2009_flu/scripts/match_k1.py`

```diff
-W = '<local project folder>'
-K = '<local data folder>/flushot-kaggle/raw/'
+W = WORK_ROOT + '/nhfs2009_flu/'
+K = SURVEY_DATA_ROOT + '/flushot-kaggle/raw/'
```

### `nhfs2009_flu/scripts/excl_k1.py`

```diff
-W = '<local project folder>'
+W = WORK_ROOT + '/nhfs2009_flu/'
```

### `nhfs2009_flu/scripts/month_k1.py`

```diff
-W = '<local project folder>'
+W = WORK_ROOT + '/nhfs2009_flu/'
```

### `nhfs2009_flu/scripts/a4_k1.py`

```diff
-W = '<local project folder>'
-K = '<local data folder>/flushot-kaggle/raw/'
+W = WORK_ROOT + '/nhfs2009_flu/'
+K = SURVEY_DATA_ROOT + '/flushot-kaggle/raw/'
```

### `nhfs2009_flu/scripts/a4_k1_summary.py`

```diff
-    g = runpy.run_path('<local project folder>')
+    g = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a4_k1.py'))
-W = '<local project folder>'
+W = WORK_ROOT + '/nhfs2009_flu/'
```

### `nhfs2009_flu/scripts/check_det.py`

```diff
-    g = runpy.run_path('consequence/a4_k1.py')
+    g = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a4_k1.py'))
```

### `independent_verification/verify2_brfss/scripts/unzip_all.py`

```diff
-B = '<local project folder>'
-V = B + '/paper9/verify2'
+B = SURVEY_DATA_ROOT
+V = WORK_ROOT + '/verify2'
-    with zipfile.ZipFile(f'{B}/data-external/brfss/{y}/LLCP{y}XPT.zip') as z:
+    with zipfile.ZipFile(f'{B}/brfss/{y}/LLCP{y}XPT.zip') as z:
-with zipfile.ZipFile(f'{B}/data-external/kaggle-heart-pytlak/heart_pytlak_archive.zip') as z:
+with zipfile.ZipFile(f'{B}/kaggle-heart-pytlak/heart_pytlak_archive.zip') as z:
```

### `independent_verification/verify2_brfss/scripts/list_cols.py`

```diff
-V = '<local project folder>'
-files = {2015: '<local data folder>/brfss/2015/xpt_unzipped/LLCP2015.XPT',
+V = WORK_ROOT + '/verify2'
+files = {2015: SURVEY_DATA_ROOT + '/brfss/2015/xpt_unzipped/LLCP2015.XPT',
```

### `independent_verification/verify2_brfss/scripts/extract_raw.py`

```diff
-V = '<local project folder>'
-files = {2015: '<local data folder>/brfss/2015/xpt_unzipped/LLCP2015.XPT',
+V = WORK_ROOT + '/verify2'
+files = {2015: SURVEY_DATA_ROOT + '/brfss/2015/xpt_unzipped/LLCP2015.XPT',
```

### `independent_verification/verify2_brfss/scripts/a_rebuild2015.py`

```diff
-V = '<local project folder>'
-K = '<local Kaggle diabetes 2015 folder>/diabetes_012_health_indicators_BRFSS2015.csv'
+V = WORK_ROOT + '/verify2'
+K = SURVEY_DATA_ROOT + '/kaggle-diabetes-2015/diabetes_012_health_indicators_BRFSS2015.csv'
```

### `independent_verification/verify2_brfss/scripts/b_rebuild2020.py`

```diff
-V = '<local project folder>'
+V = WORK_ROOT + '/verify2'
```

### `independent_verification/verify2_brfss/scripts/c_rebuild2022.py`

```diff
-V = '<local project folder>'
+V = WORK_ROOT + '/verify2'
```

### `independent_verification/verify2_brfss/scripts/c2_dk_variants.py`

```diff
-V = '<local project folder>'
+V = WORK_ROOT + '/verify2'
```

### `independent_verification/verify2_brfss/scripts/c3_subset.py`

```diff
-V = '<local project folder>'
+V = WORK_ROOT + '/verify2'
```

### `independent_verification/verify3_weighted/scripts/x_extract.py`

```diff
-B = '<local project folder>'
-V3 = B + '/paper9/verify3'
+B = SURVEY_DATA_ROOT
+V3 = WORK_ROOT + '/verify3'
-    with zipfile.ZipFile(f'{B}/data-external/brfss/{y}/LLCP{y}XPT.zip') as z:
+    with zipfile.ZipFile(f'{B}/brfss/{y}/LLCP{y}XPT.zip') as z:
-with zipfile.ZipFile(f'{B}/data-external/kaggle-heart-pytlak/heart_pytlak_archive.zip') as z:
+with zipfile.ZipFile(f'{B}/kaggle-heart-pytlak/heart_pytlak_archive.zip') as z:
-files = {2015: f'{B}/data-external/brfss/2015/xpt_unzipped/LLCP2015.XPT', 2020: f'{R}/LLCP2020.XPT', 2022: f'{R}/LLCP2022.XPT'}
+files = {2015: f'{B}/brfss/2015/xpt_unzipped/LLCP2015.XPT', 2020: f'{R}/LLCP2020.XPT', 2022: f'{R}/LLCP2022.XPT'}
```

### `independent_verification/verify3_weighted/scripts/w2015.py`

```diff
-sys.path.insert(0, '<local project folder>')
+sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
-V3 = '<local project folder>'
-K = '<local Kaggle diabetes 2015 folder>'
+V3 = WORK_ROOT + '/verify3'
+K = SURVEY_DATA_ROOT + '/kaggle-diabetes-2015'
```

### `independent_verification/verify3_weighted/scripts/wheart.py`

```diff
-sys.path.insert(0, '<local project folder>')
+sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
-V3 = '<local project folder>'
+V3 = WORK_ROOT + '/verify3'
```

### `independent_verification/brfss2021_cvd/scripts/v2_extract.py`

```diff
-P=r'<local data folder>/brfss/2021/xpt_unzipped/LLCP2021.XPT'
+P=SURVEY_DATA_ROOT + r'/brfss/2021/xpt_unzipped/LLCP2021.XPT'
```

### `independent_verification/brfss2021_cvd/scripts/v2_analyze.py`

```diff
-z=zipfile.ZipFile(r'<local data folder>/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip')
+z=zipfile.ZipFile(SURVEY_DATA_ROOT + r'/kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip')
```

### `independent_verification/nhfs/scripts/nhfs_parse.py`

```diff
-RAW = "<local data folder>/nhfs-2009/raw/"
+RAW = SURVEY_DATA_ROOT + "/nhfs-2009/raw/"
```

### `independent_verification/nhfs/scripts/explore.py`

```diff
-import sys; sys.path.insert(0, r"<local project folder>")
+import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
-pub = list(csv.DictReader(open("<local data folder>/flushot-kaggle/raw/training_set_features.csv")))+list(csv.DictReader(open("<local data folder>/flushot-kaggle/raw/test_set_features.csv")))
+pub = list(csv.DictReader(open(SURVEY_DATA_ROOT + "/flushot-kaggle/raw/training_set_features.csv")))+list(csv.DictReader(open(SURVEY_DATA_ROOT + "/flushot-kaggle/raw/test_set_features.csv")))
```

### `independent_verification/nhfs/scripts/rebuild.py`

```diff
-sys.path.insert(0, r"<local project folder>")
+sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
-OUT = "<local project folder>"
-PUB = "<local data folder>/flushot-kaggle/raw/"
+OUT = WORK_ROOT + "/verify_nhfs_independent/"
+PUB = SURVEY_DATA_ROOT + "/flushot-kaggle/raw/"
```

### `independent_verification/nhfs/scripts/scrambled_and_absent.py`

```diff
-sys.path.insert(0, r"<local project folder>")
+sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```

### `coder_agreement/scripts/s1_sample.py`

```diff
-W = '<local project folder>'
-OUT = '<local project folder>'
+W = WORK_ROOT + '/coder_agreement_inputs/'
+OUT = WORK_ROOT + '/coder_agreement/'
```

### `coder_agreement/scripts/s2_fetch_extract.py`

```diff
-OUT = '<local project folder>'
-CACHE1 = '<local project folder>'
+OUT = WORK_ROOT + '/coder_agreement/'
+CACHE1 = WORK_ROOT + '/coder_agreement_inputs/ft_cache/'
```

### `coder_agreement/scripts/s3_abstracts.py`

```diff
-OUT='<local project folder>'
+OUT=WORK_ROOT + '/coder_agreement/'
```

### `coder_agreement/scripts/s5_arxiv.py`

```diff
-OUT='<local project folder>'
+OUT=WORK_ROOT + '/coder_agreement/'
```

### `coder_agreement/scripts/s6_arxiv_sanity.py`

```diff
-OUT='<local project folder>'
+OUT=WORK_ROOT + '/coder_agreement/'
```

## Scripts copied without change

`brfss2015_diabetes/scripts/rebuild_2015.py`, `counts_uci.py`; `brfss2020_2022_heart/scripts/extract.py`, `rebuild_heart.py`, `rawcounts.py`, `extra_counts.py`, `header.py`, `inspect_kaggle.py`; `independent_verification/verify3_weighted/scripts/svy.py`; `coder_agreement/scripts/s4_kappa.py`; `figures/figure1.py`, `figures/graphical_abstract.py`. These take paths as command-line arguments or read no files.

## Other files

- Pre-stated rule files (`*/rules/*.txt`, `*.sha256`) are byte-for-byte copies; `rules/SHA256SUMS.txt` was computed from the copies and matches the original `.sha256` records. `nhfs2009_flu/rules/a4_rule_k1.txt` had no original `.sha256` file; its hash is in that folder's `SHA256SUMS.txt`.
- `brfss2015_diabetes/outputs/rebuild_2015_out.txt`, line 74: the local absolute path of the saved pickle was replaced with `<out pickle>/rebuild2015.pkl`. No other output file was edited.
- Data cards were renamed from the working names (author, project, version and date prefix/suffix removed), e.g. `datacard-cdc-diabetes-2015.md`. Content unchanged.
- The consequence rule `prestated_rule_consequence.txt` covers both the diabetes and the heart files; it is copied into both `rules/` folders. `consequence_report.md` (both files) is in `brfss2015_diabetes/outputs/`.

## Not included

- Data files of any kind (raw survey files, Kaggle/UCI/DrivenData files, pickles, parquet, JSON result dumps), PDFs, full-text caches and search results.
- Coder-agreement inputs and per-paper codes (they identify individual papers).
- `run_low.ps1` helper scripts (Windows wrappers that ran a script at low priority and redirected output to `log_*.txt`; they contain only local paths).
- The failed first run of `q2q3_heart.py` (`q2q3_heart_log_run1_failed.txt`, `q2q3_heart_err_run1_failed.txt`): the error log holds local paths; the successful rerun log is included.
- The script that wrote `raw2021_sub.pkl` and `raw2021_physment.pkl` (raw BRFSS 2021 column extracts read by the 2021 scripts) was not found among the working files.
- `missing_by_month_out.txt` and `h1_month_out.txt` (NHFS working outputs) because no script in the working folders writes them.
