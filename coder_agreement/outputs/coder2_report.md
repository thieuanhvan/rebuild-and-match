# P9 second-coder check (blind, 30% sample)

Run 2026-11-25 15:45–15:55 (+07). Aggregate numbers only; paper identities are in the `*_private*` files.

## Design
- Sampling frame: the 73 candidate records screened by the first coder (`misdesc_candidates_private.json`). The first-coder list (`misdescription_list_private.tsv`) has 9 rows; 30% of 9 would be 3, below the minimum of 8, so the frame was widened to all screened candidates.
- Stratification: by membership in the first-coder list (9) versus not listed (64), read by a script that loaded only the identifier column; the code and phrase columns were not read before coding. 30% ceiling per stratum: 3 + 20 = 23 papers. Seed 20261125; sample order shuffled to hide the stratum. Script: `scripts/s1_sample.py`.
- One listed record had no match in the candidate JSON; it stayed in the stratum and was handled through its DOI.
- Full text: Europe PMC fullTextXML (cache from the first run, otherwise fetched). Full text was available for 16 of 23; the other 7 were coded from the Europe PMC abstract.
- Coding rule: Q1 uses the BRFSS 2015 binary (253,680) or 50:50 (70,692) diabetes file; Q2 states the label coding; Q3 class 1 includes prediabetes/borderline (YES) or diabetes only (NO). Codes were written to `coder2_codes_private.tsv` (15:51) before the first coder's file was opened.

## Results
| Measure | n | Agree | Percent agreement | Cohen's kappa |
|---|---|---|---|---|
| Final misdescription status, whole sample | 23 | 23 | 1.0 | 1.0 |
| Q3, both coders Q2 = yes (strict: first coder recorded a label sentence) | 3 | 3 | 1.0 | undefined (all three YES, no variance) |
| Q3, adding the paper the first coder left unlisted (implied NO) | 4 | 4 | 1.0 | 1.0 |

- Second coder Q1 = yes: 4 of 23 (3 YES, 1 NO on Q3). The other 19 are numeric false matches (DOI or article numbers, unrelated cohorts) or papers using a different file.
- Disagreements: none on Q3 or on final status.

## Notes for the first coder (not disagreements)
- C09: uses the binary file and labels class 1 correctly as diagnosed diabetes, but it is not in the first-coder list. The list records correct descriptions only for the 3-class file. If the paper reports a denominator of "papers stating the label", this paper should be added as CORRECT.
- C02, C07, C11, C17: use the 253,680-row BRFSS 2015 heart-disease sister file, built by the same pipeline. They are outside Q1 but relevant to I349. One of them labels it "BRFSS 2022".
- The automated `uses_file` flag in the candidate JSON has many false positives (10 of the 16 sampled records flagged True use neither the diabetes nor the heart file). Only the human-coded list should be used as the first coder's code.
- Small sample, with only 3 to 4 papers in the Q3 subset: kappa is fragile and should be reported together with the raw counts.
