# P9 independent numeric verification, round 3 (verify3)

Run 25/11/2026 15:56–16:01 (machine time, `date` = Wed Nov 25 15:56:56 2026). Manuscript checked: the manuscript draft of 25 November 2026 (not edited). Python 3.13.9, pandas 2.3.3, `python -I -X utf8`, BelowNormal priority, one process at a time, no network. Own scripts in `verify3/tools/` (`x_extract.py`, `svy.py`, `w2015.py`, `wheart.py`); rebuild rules copied from `verify2/tools/` (a_rebuild2015, b_rebuild2020); nothing from `i336deep/tools` or `i349deep/tools` was opened. Raw outputs: `w2015_out.txt`, `wheart_out.txt`. Proportions truncated to 4 decimals.

Rebuild checks repeated before estimating: 2015 rebuild = 253,680 rows, multiset match 1.0 with Kaggle 012; 2020 rebuild = 319,795 rows, multiset match 1.0; 2022 with_nans row-aligned with raw (CVDINFR4 and CVDCRHD4 crosstabs pure), so the complete-case population of no_nans is taken as the complete rows of with_nans linked to raw.

Variance method: weighted ratio mean with `_LLCPWT`; Taylor linearisation, PSUs (`_PSU`) with replacement within strata (`_STSTR`); singleton strata contribute zero variance and are counted. This is the method stated in Methods 3.7. Each population was estimated as a domain on the full design (out-of-domain rows z = 0); a subset-only design was also run and gives the same truncated SE in every case. Singleton strata: 2015 0; 2020 27; 2022 110.

| Claim | Manuscript location | Earlier (first rebuild) | verify3 | Verdict |
|---|---|---|---|---|
| 2015 weighted diabetes, all valid | §4.1 Design variables; Table 2 row 1; §4.3 | 0.1050 (SE 0.0008) | 0.1050 (0.105003), SE 0.0008 (0.000869), n 440,658 | CONFIRMED |
| 2015 weighted diabetes, complete-case population | §4.1; Table 2 row 1 Note | 0.1228 (SE 0.0012) | 0.1228 (0.122805), SE 0.0012 (0.001286) | CONFIRMED |
| 2015 weighted documented label (DIABETE3 1 or 4), all valid | §4.1; Table 2 row 2 | 0.1209 (SE 0.0009) | 0.1209 (0.120994), SE 0.0009 (0.000933) | CONFIRMED |
| 2015 unweighted binary rate | §4.1; Table 2; §4.3; Abstract | 0.1393 | 35,346/253,680 = 0.1393 | CONFIRMED |
| 2015 valid label / excluded for label | §4.1 Rebuild; Fig. 1 Panel A | 440,658 / 798 | 440,658 / 798 | CONFIRMED |
| 2015 complete-case exclusions | Fig. 1 Panel A | 186,978 | 440,658 − 253,680 = 186,978 (rebuild count) | CONFIRMED |
| Binary file duplicates | §4.1 Known points; Table 1 row 2 | 24,206 (0.0954) | 24,206; 24,206/253,680 = 0.0954 | CONFIRMED |
| Three-class file duplicates | Table 1 row 1 | 23,899 | 23,899 in Kaggle 012 and in own rebuild | CONFIRMED |
| 2020 weighted _MICHD, valid respondents | §4.2 Duplicates and prevalence; Table 2; §4.3 | 0.0648 (SE 0.0008) | 0.0648 (0.064820), SE 0.0008 (0.000843), n 398,387 | CONFIRMED |
| 2020 weighted _MICHD, file population | §4.2; Table 2 | 0.0648 (SE 0.0009) | 0.0648 (0.064804), SE 0.0009 (0.000931) | CONFIRMED |
| 2020 unweighted rate | §4.2; Table 2; §4.3 | 0.0855 | 27,373/319,795 = 0.0855 | CONFIRMED |
| 2022 weighted infarction, valid respondents | §4.2; Table 2; §4.3 | 0.0441 (SE 0.0006) | 0.0441 (0.044156), SE 0.0006 (0.000619), n 442,067 | CONFIRMED |
| 2022 weighted infarction, complete-case population | §4.2; Table 2 | 0.0429 (SE 0.0007) | 0.0429 (0.042945), SE 0.0007 (0.000798) | CONFIRMED |
| 2022 unweighted rate | §4.2; Table 2; §4.3 | 0.0546 | 13,435/246,022 = 0.0546 | CONFIRMED |
| 2020-definition positives in no_nans / share HA-negative | §4.2 Outcome definition; Table 2 row 4 | 21,616; 8,181 (0.3784) | 21,616 (HA or angina in file = raw _MICHD = 1 among linked rows); 8,181/21,616 = 0.3784 | CONFIRMED |
| with_nans / no_nans duplicates | Table 1 rows 5–6 | 157 / 9 | 157 / 9 (all columns, NaN treated as equal) | CONFIRMED |
| 2020 "Other" pooling | §4.2 Race coding | NHPI 1,667; other 2,326; multiracial 6,710; 225 imputed | 1,667 / 2,326 / 6,710 / 225 (_RACE 5/6/7/9); total 10,928 = Kaggle "Other" | CONFIRMED |
| 2020 duplicates | §4.2; Table 1 row 4 | 18,078 (0.0565) | 18,078 (file and rebuild); 0.0565 | CONFIRMED |
| 2020 complete-case exclusions | Fig. 1 Panel B | 82,163 | 401,958 − 319,795 = 82,163 | CONFIRMED |
| 2022 exclusions and "don't know only" share | §4.2 Valid answers; Table 2 row 5; Fig. 1 Panel C | 98,073 of 199,110 (0.4925) | 445,132 − 246,022 = 199,110; 98,073 (count from verify2 c2_out) / 199,110 = 0.4925 | CONFIRMED |

Notes
- Methods 3.9 still says the heart weighted prevalences, the 2022 duplicate counts, the 2020 race pooling counts and the 2020-definition positives "come from the first script set only"; after this run all of them have been recomputed independently (and the 2015 weighted figures too). The sentence needs updating; the manuscript was not edited here.
- Not in the manuscript, for reference: documented label in the 2015 complete-case population = 0.1406 (SE 0.0013); 50:50 file has 1,635 duplicate rows.
- Housekeeping: `verify3/raw/` (unzipped XPT, Kaggle heart CSVs, parquet subsets) deleted at the end of the run.
