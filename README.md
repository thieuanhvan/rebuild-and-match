# Rebuild-and-Match: code release

Code, pre-stated rules and result files for the paper "Rebuild-and-Match: A Repeatable Method for Tracing the Construction of Machine Learning Benchmarks Derived from Health Surveys".

The method rebuilds a published benchmark file from the raw public survey it was derived from, matches the rebuilt rows against the published rows as multisets, records each construction rule that is needed for an exact match, and then measures whether those construction choices change model results (the consequence step). Four benchmark families are covered:

| Folder | Published benchmark | Source survey |
|---|---|---|
| `brfss2015_diabetes/` | CDC Diabetes Health Indicators (UCI id 891; Kaggle "Diabetes Health Indicators Dataset", three CSV files) | BRFSS 2015 |
| `brfss2020_2022_heart/` | Kaggle "Personal Key Indicators of Heart Disease" (heart_2020_cleaned, heart_2022_with_nans, heart_2022_no_nans) | BRFSS 2020 and 2022 |
| `brfss2021_cvd/` | Kaggle "Cardiovascular Diseases Risk Prediction Dataset" (CVD_cleaned.csv) | BRFSS 2021 |
| `nhfs2009_flu/` | DrivenData "Flu Shot Learning" (training/test features, training labels) | National 2009 H1N1 Flu Survey (NHFS) |

Other folders:

- `independent_verification/`: second, separately written sets of scripts that recompute the main counts (`verify2_brfss/`: rebuilds of 2015, 2020, 2022; `verify3_weighted/`: survey-weighted prevalences with Taylor-linearised standard errors; `brfss2021_cvd/`: 2021 rebuild check; `nhfs/`: NHFS parse, recode, match and scrambled-column check).
- `coder_agreement/`: scripts and aggregate report for the blind second-coder check of how published papers describe the diabetes label.
- `figures/`: scripts that draw Figure 1 and the graphical abstract.
- `datacards/`: data cards for the four benchmark families.

Each dataset folder has `scripts/` (code), `outputs/` (the result files cited in the paper, as produced by the scripts) and `rules/` (pre-stated rules, written and hashed before the analysis they govern; `rules/SHA256SUMS.txt` lists their hashes, and the original `.sha256` files are kept unchanged).

## Data are not included

No survey microdata and no copy of any published benchmark file is redistributed here. Download them yourself from the original sources:

- BRFSS annual data (CDC), SAS transport zip files `LLCP2015XPT.zip`, `LLCP2020XPT.zip`, `LLCP2021XPT.zip`, `LLCP2022XPT.zip`, from the annual-data pages:
  https://www.cdc.gov/brfss/annual_data/annual_2015.html,
  https://www.cdc.gov/brfss/annual_data/annual_2020.html,
  https://www.cdc.gov/brfss/annual_data/annual_2021.html,
  https://www.cdc.gov/brfss/annual_data/annual_2022.html
- NHFS public-use file (CDC/NCHS): https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/nis/nhfs/ (`nhfspuf.dat`, `nhfspuf.sas`, documentation)
- UCI Machine Learning Repository dataset 891, `data.csv`: https://doi.org/10.24432/C53919
- Kaggle "Diabetes Health Indicators Dataset" (alexteboul): https://www.kaggle.com/datasets/alexteboul/diabetes-health-indicators-dataset
- Kaggle "Personal Key Indicators of Heart Disease" (kamilpytlak): https://www.kaggle.com/datasets/kamilpytlak/personal-key-indicators-of-heart-disease
- Kaggle "Cardiovascular Diseases Risk Prediction Dataset" (alphiree): https://www.kaggle.com/datasets/alphiree/cardiovascular-diseases-risk-prediction-dataset
- DrivenData "Flu Shot Learning" (competition 66): https://www.drivendata.org/competitions/66/flu-shot-learning/

Use of these files is subject to the terms on each source page.

## Expected layout under SURVEY_DATA_ROOT

Scripts read raw and published files from the folder named by the environment variable `SURVEY_DATA_ROOT`, and write intermediate files and outputs under `WORK_ROOT` (default `./work`).

```
SURVEY_DATA_ROOT/
  brfss/
    uci-891/data.csv
    2015/xpt_unzipped/LLCP2015.XPT        (unzipped from LLCP2015XPT.zip)
    2020/LLCP2020XPT.zip
    2021/LLCP2021XPT.zip
    2021/xpt_unzipped/LLCP2021.XPT
    2022/LLCP2022XPT.zip
  kaggle-diabetes-2015/
    diabetes_012_health_indicators_BRFSS2015.csv
    diabetes_binary_health_indicators_BRFSS2015.csv
    diabetes_binary_5050split_health_indicators_BRFSS2015.csv
  kaggle-heart-pytlak/heart_pytlak_archive.zip   (the Kaggle archive, renamed)
  kaggle-cvd-2021/raw/cvd_risk_prediction_archive.zip   (contains CVD_cleaned.csv)
  flushot-kaggle/raw/
    training_set_features.csv
    training_set_labels.csv
    test_set_features.csv
  nhfs-2009/raw/
    nhfspuf.dat
    nhfspuf.sas
```

Some scripts take file paths as command-line arguments instead (their usage line is in the docstring). Create the `WORK_ROOT` subfolders named in each script before running it (for example `WORK_ROOT/consequence/out/`).

## Software

Python 3.13 (results were produced with 3.13.9). See `requirements.txt`. Run scripts as `python -I -X utf8 <script>`. Proportions in the outputs are truncated to four decimals.

## How to run, in order

Linux/macOS: `export SURVEY_DATA_ROOT=/data/surveys WORK_ROOT=/data/work`. Windows PowerShell: `$env:SURVEY_DATA_ROOT='<path to the data folder>'`.

### 1. BRFSS 2015 diabetes (`brfss2015_diabetes/`)

1. `rebuild_2015.py <LLCP2015.XPT> <uci data.csv> <kaggle diabetes dir> <out.pkl>`: rebuilds the file from raw BRFSS 2015 and matches it against the UCI and Kaggle files. Output: `outputs/rebuild_2015_out.txt`.
2. `counts_uci.py <uci data.csv>`: column and label counts of the UCI file. Output: `outputs/d3_counts_uci891.txt`.
3. `verify_independent_i336.py`: separately written re-check of the core counts. Output: `outputs/verify_independent_i336_out.txt`.
4. `q1_diabetes.py`: consequence step for the diabetes file under `rules/prestated_rule_consequence.txt`. Output: `outputs/q1_diabetes_log.txt`; `outputs/consequence_report.md` summarises the consequence step for both the diabetes and the heart files.

### 2. BRFSS 2020/2022 heart (`brfss2020_2022_heart/`)

1. `header.py <XPT>` and `inspect_kaggle.py <csv>`: list raw columns and Kaggle file shapes.
2. `extract.py <LLCP20xx.XPT> <raw.pkl> <col> [col ...]`: saves the needed raw columns.
3. `rawcounts.py <raw.pkl>`: raw value counts.
4. `rebuild_heart.py <2020|2022> <raw.pkl> <unzipped kaggle dir> <out.pkl>`: rebuild and match. Outputs: `outputs/rebuild_2020_out.txt`, `outputs/rebuild_2022_out.txt`.
5. `extra_counts.py <rebuilt 2020 pkl> <rebuilt 2022 pkl>`: supplementary cross-tabulations. Output: `outputs/extra_counts_out.txt`.
6. `q2q3_heart.py`: consequence step for the heart files (reads `heart_2020_cleaned.csv` and `heart_2022_no_nans.csv` from `WORK_ROOT/consequence/work/2020/` and `.../2022/`). Output: `outputs/q2q3_heart_log.txt`.

### 3. BRFSS 2021 CVD (`brfss2021_cvd/`)

The scripts read `raw2021_sub.pkl` and `raw2021_physment.pkl` (raw BRFSS 2021 columns) from `WORK_ROOT/brfss2021_cvd/`. Step 0 below writes them; it was added for this release and was checked to reproduce the original pickles exactly (438,693 rows, all values equal).

0. `extract_raw2021.py`: reads `SURVEY_DATA_ROOT/brfss/2021/LLCP2021.XPT` and writes `raw2021_sub.pkl` and `raw2021_physment.pkl` to `WORK_ROOT/brfss2021_cvd/`; every 2021 script reads these two files.
1. `rebuild_cvd2021_v1.py`: first rebuild under hypothesis H1 (writes `rebuild_h1_all.pkl`).
2. `rebuild_cvd2021_search.py`, `rebuild_cvd2021_sequential.py`, `find_extra_rule.py`, `find_extra_rule2.py`: the search for the conversion and exclusion rules (kept for transparency).
3. `rebuild_cvd2021_final.py`: final rebuild with exact multiset match. Output: `outputs/counts_i360_out.txt`.
4. `a4_i360.py`: consequence step under `rules/a4_rule_i360.txt`. Output: `outputs/a4_i360_out.txt`.
5. `a4_q3_sensitivity.py` (post hoc, labelled as such) and `weighted_2021.py` (weighted prevalence). Outputs: `outputs/a4_q3_sensitivity_out.txt`, `outputs/weighted_2021_out.txt`.

### 4. NHFS flu (`nhfs2009_flu/`)

1. `read_nhfs.py`: parses the fixed-width NHFS file with the layout in `nhfspuf.sas`.
2. `rebuild_k1.py`, `match_k1.py`, `excl_k1.py`, `month_k1.py`: rebuild, multiset match, description of absent adults, and shares by interview month. Outputs: `outputs/rebuild_k1_out.txt`, `match_k1_out.txt`, `excl_k1_out.txt`, `month_k1_out.txt`.
3. `a4_k1.py`: consequence step under `rules/a4_rule_k1.txt` (single-threaded BLAS for reproducibility). Outputs: `outputs/a4_k1_out.txt` and `a4_k1_out_rerun.txt` (identical reruns); `a4_k1_out_run1_multithread.txt` and `a4_k1_out_run2_multithread.txt` show the run-to-run difference before threads were fixed. `check_det.py` reruns `a4_k1.py` to check determinism.
4. `a4_k1_summary.py`: five-split medians and ranges and weighted label shares. Output: `outputs/a4_k1_summary_out.txt`.

### 5. Independent verification (`independent_verification/`)

- `verify2_brfss/`: `unzip_all.py`, `list_cols.py`, `extract_raw.py`, then `a_rebuild2015.py`, `b_rebuild2020.py`, `c_rebuild2022.py`, `c2_dk_variants.py`, `c3_subset.py`. Outputs `a_out.txt` to `c3_out.txt`; summary `verify2_report.md`.
- `verify3_weighted/`: `x_extract.py`, then `w2015.py` and `wheart.py` (both import `svy.py`). Outputs `w2015_out.txt`, `wheart_out.txt`; summary `verify3_report.md`.
- `brfss2021_cvd/`: `v2_extract.py` then `v2_analyze.py` (both use `v2_raw.pkl` in the current directory). Output `v2_analyze_out.txt`.
- `nhfs/`: `nhfs_parse.py` (module), `explore.py`, `rebuild.py`, `scrambled_and_absent.py`; recode rules in `rules/recode_rules.txt`. Outputs `rebuild_out.txt`, `scrambled_out.txt`; summary `report.txt`.

### 6. Coder agreement (`coder_agreement/`)

`s1_sample.py` (blind stratified sample), `s2_fetch_extract.py` and `s3_abstracts.py` (Europe PMC full text and abstracts; network access), `s4_kappa.py` (agreement and Cohen's kappa), `s5_arxiv.py` and `s6_arxiv_sanity.py` (arXiv searches; network access). The input lists and per-paper codes identify individual papers and are not released; only the aggregate report `outputs/coder2_report.md` is included.

### 7. Figures (`figures/`)

`python -I -X utf8 figure1.py <out dir>` and `python -I -X utf8 graphical_abstract.py <out dir>` write PNG and PDF files. The numbers drawn are typed into the scripts from the outputs above.

## SHA-256 of the expected source files

From the data cards and the download records:

| File | SHA-256 |
|---|---|
| UCI 891 data.csv | 9f71fda9d4ae5f4878c99b9233b6a16accfa9a17c194116a6b78100540934964 |
| diabetes_012_health_indicators_BRFSS2015.csv | a971809d0786d2d7d7f6070f83dfe8af9d860ea33a79e0e2701c8a49f78f9861 |
| diabetes_binary_health_indicators_BRFSS2015.csv | 19f367e3e3350768f0c144c5d73ee5b355f67a57eaaa86ca7bd8aec594d8b1d0 |
| diabetes_binary_5050split_health_indicators_BRFSS2015.csv | 873128ba0264d66a8b09bb6158f21fd4bedc10459d1ed5ecad3b94167a9539b4 |
| heart_2020_cleaned.csv | 90a1e2e8bdcb4aba54314a41d35d2ac3be4763e459df33951e08e415f527f5a8 |
| heart_2022_with_nans.csv | 9c5be2d641c60b63d395cb374581e4a691dbfe3cf0258dc437535b79e7a30a79 |
| heart_2022_no_nans.csv | f5eddf47d85170f2f7bc3ba523c275d705ddf22518f95d50aa33ddcfd786a94f |
| heart_pytlak_archive.zip (Kaggle archive) | 682bf01c95e57c0bb8b023d5ee9c88b01a070791fbf8f20801447b1952439dcd |
| CVD_cleaned.csv | 0c3c399c95c9df8ba65fa36821a95c8f27609508dc6927b6a6e7034f25a492c8 |
| training_set_features.csv | 9a805f24b45fd9bd0b52cedf7cab0ccc62b512372f00151b028b004b0973d1e5 |
| training_set_labels.csv | 0ad33a821b96666a0dbfafc4e6fe23969ded212c6b55eb8763bd8bd78b8cae40 |
| test_set_features.csv | fbb8e4f208c222a1559c701dd351e5db8fc12c1671393a009bdc055830fa42b5 |
| submission_format.csv | 9a6cfd8e7d75f4d0586f59ec50d27947c5c2d546e25db80bce29df53ebee3a35 |
| nhfspuf.dat | f6c0890bbeae08861966498cffb32c78202059dcf9b929d7e8c063330120f7b4 |
| nhfspuf.sas | a4ee4ca5c589ffd164c6cb8d5a446ca466bb0e60f102207e214a68ecc46ccbbb |
| nhfspuf_readme.txt | 3a0964281aa1167a092ecbde70e2ffe28da2a76a9d8747025ce65641be26f736 |
| nhfspuf_CODEBOOK.PDF | 066e802e23e9c8da961738501106489badeb3270721be06686babbf9fecc7204 |
| nhfspuf_DUG.PDF | aedca386f06b6af1daa7925501cbcf363094374ea43767d15702daf24ab91eb7 |
| nhfspuf_QUEX.PDF | f19e1cf8f1c5d26633deb1329c1299b9876324387ae89df4760f500bc023d4db |
| LLCP2015XPT.zip | 38bfd48c64b99328c67feac36cedfff6f2991d49e89c4ffd549083cb626764f0 |
| LLCP2020XPT.zip | 132269948a09506392c417c4042c052f088c86334ee3bc34c2776501f240b4b6 |
| LLCP2021XPT.zip | e8a6e290cdcb6bff82d8f37dff6c3f3e435d428191eb529a716cf9f5316aa621 |
| LLCP2022XPT.zip | b6319c949b7289f8020fc903c3c2d38fe7e0b28ad703dcd81547f5cd0c0dcfeb |

The BRFSS zip files were downloaded on 25 November 2026; CDC may replace files on its pages, so a different hash means a different release of the file.

## NHFS acknowledgement and disclaimer

This work uses the National 2009 H1N1 Flu Survey (NHFS) public-use data file. The original data source is the Centers for Disease Control and Prevention (CDC): the National Center for Health Statistics (NCHS) and the National Center for Immunization and Respiratory Diseases (NCIRD).

Source: CDC, NCIRD and NCHS (2012), National 2009 H1N1 Flu Survey.

Reference: U.S. Department of Health and Human Services (DHHS). National Center for Health Statistics. The National 2009 H1N1 Flu Survey. Hyattsville, MD: Centers for Disease Control and Prevention, 2012.

All analyses, interpretations and conclusions in this repository and the paper are those of the author, not of NCHS, which is responsible only for the initial data. The NHFS data-use restrictions in the file's readme apply: the data may be used for statistical reporting and analysis only, no attempt may be made to identify any person, and the files may not be linked with individually identifiable data.

The BRFSS data are collected by CDC and the state health departments; CDC is not responsible for the analyses here.

## License

Code and text in this repository: MIT License (see `LICENSE`). The license does not cover the third-party data described above.

## Labels in file names

Names such as `i336`, `i349`, `i360` and `k1` are the working labels of the four analyses (diabetes 2015, heart 2020 and 2022, cardiovascular 2021, flu). The files in each `rules/` folder are kept byte for byte, because their SHA-256 hashes were recorded before the models were fitted; they therefore keep these labels and the original wording.

