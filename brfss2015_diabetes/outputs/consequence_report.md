# P9 consequence layer: what the construction defects change for a typical user

Run 25/11/2026, 16:13 to 16:50 (SEAST). Pre-stated rule: `prestated_rule_consequence.txt`, sha256 `dfcdd348ca75c718b311d8b1d30a6f5a618083f17401458f5ae1b99a9a7732ab`, hashed 16:14:46, before any model was fitted. Scripts: `tools/q1_diabetes.py`, `tools/q2q3_heart.py` (Python 3.13, scikit-learn 1.7.2, LightGBM 4.7.0, statsmodels 0.14.5; below-normal priority, n_jobs 4). Raw outputs: `out/q1_diabetes.json`, `out/q2q3_heart.json`, `out/*_log.txt`. All analyses are unweighted, as users use the files. Numbers are truncated to four decimals. "Median [range]" is over 5 seeds (stratified 70/30 splits, seeds 20261125 to 20261129).

## Verdict summary

| Question | Pre-stated criterion (short) | Verdict |
|---|---|---|
| Q1a Prediabetes respondents under the actual label | (i) prediabetes sensitivity Wilson CI below diabetes sensitivity CI, all seeds, both models, both thresholds; AND (ii) documented-label sensitivity at least 0.02 lower than actual-label sensitivity, all seeds | INCONCLUSIVE ((i) met, (ii) missed: 0.0160 to 0.0207) |
| Q1b AUC, documented vs actual label | AUC rule: median paired difference >= 0.01, beyond seed floor, bootstrap CI excludes 0 | NOT MATERIAL (-0.0044 LR, -0.0050 LGBM) |
| Q1c Calibration-in-the-large against the documented label | abs(CITL) >= 0.01 in all seeds, both families | MATERIAL (-0.0184 / -0.0183; near-arithmetic, stated in advance) |
| Q1d Top-10 feature ranking | median top-10 overlap < 7 and below within-label floor | NOT MATERIAL (overlap 10/10 in every seed) |
| Q2a HadAngina co-feature (2022) | AUC rule on with-minus-without, or HadAngina ranked 1st in >= 4/5 seeds with share >= 0.25 | MATERIAL (both arms of the criterion) |
| Q2b 2020-definition label on the 2022 file | AUC rule on AUC(y20) - AUC(MI) | NOT MATERIAL (+0.0043 LR, +0.0051 LGBM) |
| Q3 Alcohol variable 2020 vs 2022 | adjusted OR CIs do not overlap, or crude/adjusted sign change | MATERIAL (non-overlap; same direction) |

Overall: the diabetes label documentation error changes how prediabetes cases are read and the calibration a reader would see, but not the discrimination or the feature ranking a typical user reports. In the heart file, the retained angina column moves AUC by about 0.045 and takes about 40 to 50% of the permutation importance; the definition change of the outcome itself barely moves AUC. The alcohol variable change shifts the adjusted odds ratio beyond its confidence interval, without reversing its direction.

## Q1 Diabetes file (BRFSS 2015, 253,680 rows; actual label = Diabetes_012 == 2, documented label = Diabetes_012 in {1, 2})

Pre-stated criteria: see table above and rule file, section Q1.

Result. Prevalence 0.1393 (actual) vs 0.1575 (documented). Each test set holds 1,389 prediabetes and 10,604 diabetes respondents. With models trained on the actual label, prediabetes respondents are flagged at a rate between that of respondents without diabetes and that of respondents with diabetes: at the prevalence threshold, 0.2800 (LR) and 0.2850 (LGBM) against 0.4257 and 0.4470 for diabetes and 0.0880 and 0.0841 for no diabetes. At the 0.5 threshold, only 0.0777 and 0.0755 of prediabetes respondents are flagged. Criterion (i) held in every seed. Criterion (ii) did not: the sensitivity a reader trusting the documentation would compute (positives = prediabetes or diabetes) is lower than the actual-label sensitivity by 0.0170 (LR, range 0.0160 to 0.0197) and 0.0184 (LGBM, range 0.0177 to 0.0207), just under the pre-stated 0.02; prediabetes is only 11.5% of the documented positives, so it dilutes the sensitivity little. AUC on the documented label is lower than on the actual label by 0.0044 (LR; seed floor 0.0026; bootstrap CI -0.0060 to -0.0029) and 0.0050 (LGBM; floor 0.0027; CI -0.0065 to -0.0031): detectable, below the 0.01 materiality bound. Cross-evaluation gives the same picture (actual-label model on documented label: 0.8176 LR, 0.8259 LGBM). Mean predicted risk of actual-label models is 0.139 against a documented-label event rate of 0.1575 (CITL -0.0184 LR, -0.0183 LGBM), close to the arithmetic 4,631/253,680 = 0.0182. The top-10 permutation-importance features are the same set under both labels in every seed and family (10/10; Kendall tau-b 0.9142 LR, 0.8761 LGBM), led by general health, BMI, age and high blood pressure.

Verdicts: Q1a INCONCLUSIVE; Q1b NOT MATERIAL; Q1c MATERIAL (arithmetic); Q1d NOT MATERIAL.

Manuscript-ready text. To gauge what the label misstatement changes for a typical user, we trained logistic regression and LightGBM with default settings on the binary file as distributed and on the documented label (prediabetes or diabetes), with five stratified 70/30 splits and criteria fixed before fitting. Discrimination and feature rankings were practically unchanged: the AUC under the documented label was 0.0044 (logistic regression) and 0.0050 (LightGBM) lower, below the pre-stated bound of 0.01, and the ten most important features were identical in every split. The misstatement matters for how individual predictions are read. A model trained on the file flags 0.2800 to 0.2850 of respondents with prediabetes at the threshold that matches the file prevalence, and 0.0755 to 0.0777 at the 0.5 threshold, whereas a reader who trusts the documentation would count all of them as positives; its mean predicted risk is 0.0183 below the documented-label event rate. Prediabetes respondents behave as an intermediate group, flagged three times as often as respondents without diabetes but clearly less often than those with diabetes, which a binary label documented as "prediabetes or diabetes" hides.

Table C1. Diabetes file: consequences of the label misstatement (median [range] over 5 splits).

| Quantity | Logistic regression | LightGBM |
|---|---|---|
| AUC, trained and evaluated on actual label | 0.8224 [0.8211, 0.8237] | 0.8307 [0.8288, 0.8316] |
| AUC, trained and evaluated on documented label | 0.8180 [0.8148, 0.8187] | 0.8257 [0.8224, 0.8262] |
| Difference (documented - actual); bootstrap 95% CI, split 1 | -0.0044; [-0.0060, -0.0029] | -0.0050; [-0.0065, -0.0031] |
| Flagged at 0.5: prediabetes / diabetes / no diabetes | 0.0777 / 0.1570 / 0.0205 | 0.0755 / 0.1575 / 0.0172 |
| Flagged at prevalence threshold: prediabetes / diabetes / no diabetes | 0.2800 / 0.4257 / 0.0880 | 0.2850 / 0.4470 / 0.0841 |
| Sensitivity against documented label at prevalence threshold | 0.4076 | 0.4280 |
| Calibration-in-the-large against documented label | -0.0184 | -0.0183 |
| Top-10 feature overlap (documented vs actual); Kendall tau-b | 10/10; 0.9142 | 10/10; 0.8761 |

Wilson 95% CIs for prediabetes sensitivity (n = 1,389 per split), split 1, prevalence threshold: LR 0.2699 [0.2472, 0.2939]; LGBM 0.2850 [0.2619, 0.3094]; per-split CIs in `out/q1_diabetes.json`.

## Q2 Heart file 2022 (heart_2022_no_nans, 246,022 rows)

Pre-stated criteria: AUC rule for D2 = AUC(M1, with HadAngina) - AUC(M2, without), or HadAngina ranked 1st in >= 4/5 seeds with median importance share >= 0.25 (Q2a); AUC rule for D3 = AUC(M3 on the 2020-definition label y20 = HadHeartAttack or HadAngina, both removed as features) - AUC(M2) (Q2b).

Result. Q2a: keeping HadAngina raises the AUC for HadHeartAttack from 0.8423 to 0.8870 (LR; D2 0.0441, seed floor 0.0072, bootstrap CI 0.0365 to 0.0428) and from 0.8432 to 0.8891 (LGBM; D2 0.0453, floor 0.0050, CI 0.0375 to 0.0447). HadAngina is the most important feature in 5/5 seeds for both models, with a median share of the summed positive permutation importance of 0.4130 (LR) and 0.4717 (LGBM); in split 1 its importance is 1.5 (LR) and 2.3 (LGBM) times that of the next feature, age category. Q2b: the 2020-definition label has prevalence 0.0878 (21,616 positives) against 0.0546 (13,435); a model trained on it reaches AUC 0.8467 (LR) and 0.8477 (LGBM), only 0.0043 and 0.0051 above the infarction-only model without angina (CIs 0.0006 to 0.0082 and 0.0016 to 0.0095, both inside the ±0.01 band). For reference, the 2020 file gives AUC 0.8394 (LR) and 0.8416 (LGBM) on its own label (descriptive only).

Verdicts: Q2a MATERIAL; Q2b NOT MATERIAL.

Manuscript-ready text. In the 2022 complete-case file, models for HadHeartAttack that keep HadAngina as a feature reach an AUC of 0.8870 (logistic regression) and 0.8891 (LightGBM), against 0.8423 and 0.8432 without it, a gain of 0.0441 and 0.0453 that is six to nine times the variation across splits. HadAngina was the most important feature in all ten fitted models, accounting for a median 0.4130 and 0.4717 of the total permutation importance. Redefining the outcome as in 2020 (infarction or coronary heart disease) raises prevalence from 0.0546 to 0.0878 but changes the AUC by only 0.0043 to 0.0051 when angina is not used as a feature. The AUC gain users report on the 2022 file over the 2020 file (0.8394 to 0.8416) is therefore largely carried by one label-adjacent co-feature rather than by the change of outcome definition, and results from the two versions are not comparable as "heart disease prediction".

Table C2. Heart file 2022: angina co-feature and outcome definition (median [range] over 5 splits).

| Quantity | Logistic regression | LightGBM |
|---|---|---|
| M1 HadHeartAttack, all 39 features (as distributed): AUC | 0.8870 [0.8864, 0.8876] | 0.8891 [0.8876, 0.8900] |
| M2 HadHeartAttack, HadAngina removed: AUC | 0.8423 [0.8409, 0.8482] | 0.8432 [0.8420, 0.8471] |
| D2 = M1 - M2; bootstrap 95% CI, split 1 | 0.0441; [0.0365, 0.0428] | 0.0453; [0.0375, 0.0447] |
| HadAngina rank in M1; median importance share | 1st in 5/5; 0.4130 | 1st in 5/5; 0.4717 |
| M3 2020-definition label (prevalence 0.0878), both items removed: AUC | 0.8467 [0.8450, 0.8522] | 0.8477 [0.8467, 0.8523] |
| D3 = M3 - M2; bootstrap 95% CI, split 1 | 0.0043; [0.0006, 0.0082] | 0.0051; [0.0016, 0.0095] |
| Reference: heart_2020_cleaned, HeartDisease (prevalence 0.0855): AUC | 0.8394 [0.8370, 0.8432] | 0.8416 [0.8408, 0.8457] |

Note: the split-1 bootstrap CI of D2 lies slightly below the 5-split median because split 1 has the smallest D2 (0.0392 LR, 0.0408 LGBM).

## Q3 Alcohol variable (2020 AlcoholDrinking = heavy drinking; 2022 AlcoholDrinkers = any drinking in 30 days)

Pre-stated criterion: MATERIAL if the age- and sex-adjusted OR 95% CIs of 2020 and 2022 do not overlap, or crude and adjusted ORs lie on opposite sides of 1 with both CIs excluding 1.

Result. "Yes" share 0.0680 (2020) vs 0.5499 (2022). Outcome rate Yes vs No: 0.0523 vs 0.0880 (2020, HeartDisease); 0.0393 vs 0.0732 (2022, HadHeartAttack). Crude OR 0.5728 [0.5390, 0.6088] (2020) and 0.5184 [0.5003, 0.5372] (2022); adjusted for age category and sex 0.7258 [0.6817, 0.7728] (2020) and 0.5699 [0.5494, 0.5913] (2022). The adjusted CIs do not overlap. Using the 2020-definition outcome in the 2022 file gives 0.6171 [0.5990, 0.6357] adjusted, still outside the 2020 interval, so the shift is not explained by the outcome change alone. No sign change: the inverse association is present in both versions, crude and adjusted.

Verdict: MATERIAL (by the non-overlap arm; direction unchanged).

Manuscript-ready text. The alcohol column changes meaning between versions: in 2020 it is the CDC heavy-drinking indicator (Yes in 0.0680 of rows), in 2022 any drinking in the past 30 days (Yes in 0.5499). In both versions respondents answering "Yes" have a lower outcome rate, the pattern a user of the 2020 file questioned on the dataset's discussion page. Adjusted for age group and sex, the odds ratio is 0.7258 (95% CI 0.6817 to 0.7728) in 2020 and 0.5699 (0.5494 to 0.5913) in 2022, and 0.6171 (0.5990 to 0.6357) in 2022 when the 2020 outcome definition is applied, so the two versions give non-overlapping estimates for what users read as the same variable. These are unweighted, descriptive associations in convenience subsamples of a cross-sectional survey; they are not causal effects, and the inverse direction is compatible with confounding and with people with heart disease reducing alcohol use.

Table C3. Alcohol and heart outcome, unweighted logistic regression (full files).

| File and outcome | Alcohol variable (Yes share) | Outcome rate Yes / No | Crude OR (95% CI) | Age- and sex-adjusted OR (95% CI) |
|---|---|---|---|---|
| heart_2020_cleaned, HeartDisease (n = 319,795) | AlcoholDrinking, heavy drinking (0.0680) | 0.0523 / 0.0880 | 0.5728 (0.5390, 0.6088) | 0.7258 (0.6817, 0.7728) |
| heart_2022_no_nans, HadHeartAttack (n = 246,022) | AlcoholDrinkers, any drinking (0.5499) | 0.0393 / 0.0732 | 0.5184 (0.5003, 0.5372) | 0.5699 (0.5494, 0.5913) |
| heart_2022_no_nans, 2020-definition outcome | AlcoholDrinkers (0.5499) | 0.0662 / 0.1142 | 0.5498 (0.5344, 0.5655) | 0.6171 (0.5990, 0.6357) |

## Deviations and caveats

- Q2/Q3 script, first run (16:15 to 16:33): it crashed in Q3 because the global path variable `C` shadowed the formula function `C()` of patsy; nothing was saved. The variable was renamed, nothing else changed, and the whole script was rerun (16:35 to 16:49). The failed logs are kept as `out/q2q3_heart_*_run1_failed.txt`. The Q2 verdicts printed in run 1 equal those of run 2.
- In `q1_diabetes.json` the numeric prevalence-threshold value was overwritten by the per-group dict under the same key `t2`; the flagged shares (`flag_share`, 0.1372 to 0.1412 for actual-label models, 0.1555 to 0.1599 for documented-label models) confirm that the threshold matched the training prevalence as pre-stated.
- Q1a fails criterion (ii) narrowly (0.0160 to 0.0207 vs 0.02); reported as INCONCLUSIVE per the rule, not reinterpreted.
- Q1c is close to arithmetic (stated in the rule beforehand); it should not be presented as an independent finding.
- The optional weighted sensitivity line was not run (not pre-stated). No causal reading of Q3.
- The unzipped heart files in `work/` were deleted after the run; the source zip is unchanged.
