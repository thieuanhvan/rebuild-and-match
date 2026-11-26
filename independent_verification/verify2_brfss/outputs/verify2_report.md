# P9 independent numeric verification (verify2)

Run 25/11/2026 15:30–16:10 (machine time). Own scripts in `verify2/tools/` (written before opening any earlier tool or `*_out.txt`); raw outputs `a_out.txt`, `b_out.txt`, `c_out.txt`, `c2_out.txt`, `c3_out.txt`. Python 3.13.9, pandas 2.3.3, all runs at BelowNormal priority, one process at a time, no network. Proportions truncated to 4 decimals.

Rebuild status:
- 2015 diabetes_012: own rebuild = 253,680 rows, multiset match **1.0** (0 differing tuples) with the Kaggle 012 file. BMI = `(_BMI5/100).round(0)` (pandas half-to-even); a half-up rounding gives 0.9933, so the Kaggle file uses half-to-even.
- 2020 heart_2020_cleaned: own rebuild = 319,795 rows, multiset match **1.0** (Race = `_IMPRACE`, HeartDisease = `_MICHD`, DK/refused/missing on any of 18 columns dropped).
- 2022 heart_2022_with_nans: row-aligned with raw LLCP2022 (445,132 = 445,132); every cell of all 40 columns agrees with a deterministic recode of the raw variable (category labels learned by crosstab, purity 1.0 for every code). `no_nans` = complete cases of `with_nans` (246,022, multiset match 1.0), so file rows link to raw rows exactly.

| Claim | Earlier value | My value | Verdict | Note |
|---|---|---|---|---|
| A. 2015 rebuild vs Kaggle 012 | 1.0 | 1.0 (253,680) | MATCH | |
| A. kept DIABETE3 = 2 (gestational only, labelled 0) | 1,978 | 1,978 | MATCH | |
| A. kept prediabetes (DIABETE3 = 4) | 4,631 | 4,631 | MATCH | equals Kaggle class 1 |
| A. complete-case retention | 253,680/441,456 | 253,680/441,456 = 0.5746 | MATCH | |
| B. HeartDisease = `_MICHD` | yes | yes | MATCH | raw: `_MICHD`=1 iff CVDINFR4=1 or CVDCRHD4=1 (0 exceptions) |
| B. HD=Yes with CVDINFR4 ≠ 1 | 9,874/27,373 (0.3607) | 9,874/27,373 = 0.3607 | MATCH | 9,675 answered "No" MI, 192 DK, 6 refused, 1 missing |
| C. respondents with ≥1 DK turned NaN | 89,232 | 89,232 only under the earlier definition | MATCH (narrow definition) | 89,232 = DK (7) on PNEUVAC4, TETANUS1, LCSCTSC1, HIVTST7, COVIDPOS **plus CHECKUP1 = 8 "never"** (not a DK). DK on all 32 raw source variables = 124,631; DK or refused = 167,259. Wording in the paper must name the definition |
| C. none of them in no_nans | 0 | 0 (all three definitions) | MATCH | every DK cell is NaN in with_nans |
| C. race DK/refused in raw | 14,057 | 14,055 (`_RACEGR4` = 9) + 2 blank `_RACEGR4` | MISMATCH in label | 14,057 is the count of NaN race in with_nans, not of DK/refused codes |
| C. with_nans RaceEthnicityCategory NaN | 14,055 | 14,057 | MISMATCH in label | the two numbers are swapped. Gap of 2 = two raw records with `_RACEGR4` and `_RACE1` blank (no code), which also become NaN |
| C. 2022 Other race only NH in no_nans | 12,205 | 12,205 | MATCH | |
| C. = Asian + AIAN + NHPI | 6,813 + 3,895 + 1,497 | 6,813 + 3,895 + 1,497 (`_RACE1` 4/3/5) | MATCH | no `_RACE1` = 6 "other race" rows in this category |
| D. 2020 file rows with `_RACE` = 9 but imputed race | 4,510 | 4,510 | MATCH | raw: 8,987 with `_RACE` = 9 |
| D. of which White | 3,997 | 3,997 | MATCH | others: Other 225, Black 110, AIAN 77, Asian 59, Hispanic 42 |

After my numbers were fixed I opened `i349deep/tools/rebuild_heart.py` (lines 182–186), `i349deep/rebuild_2022_out.txt`, `i349deep/rebuild_2020_out.txt`, `i336deep/rebuild_2015_out.txt`: they agree with the table above; the 89,232 definition was taken from line 182–183 of the earlier tool and recomputed in my `c3_subset.py`.

Housekeeping: `verify2/raw/` holds the unzipped LLCP2020.XPT and LLCP2022.XPT (about 2 GB) and the column-subset parquet files; the XPT files can be deleted.
