# Corrected Data Card: Personal Key Indicators of Heart Disease (BRFSS 2020 and 2022)

Applies to: Kaggle dataset Personal Key Indicators of Heart Disease (https://www.kaggle.com/datasets/kamilpytlak/personal-key-indicators-of-heart-disease), files heart_2020_cleaned.csv, heart_2022_with_nans.csv and heart_2022_no_nans.csv (archive members dated 12 October 2023; the archive does not state a Kaggle version number, so the copy is identified by the SHA-256 hashes below). This card adds construction facts to the existing documentation; it does not replace the data. Licence: CC0: Public Domain according to the Kaggle dataset page (read 25 November 2026).

## Source and rebuild

| File | BRFSS source | Raw respondents | Rows (share) | Rebuild |
|---|---|---|---|---|
| heart_2020_cleaned | 2020 LLCP, https://www.cdc.gov/brfss/annual_data/annual_2020.html | 401,958 | 319,795 (0.7955) | multiset match 1.0; 18 columns; "don't know", refused and missing dropped |
| heart_2022_with_nans | 2022 LLCP, https://www.cdc.gov/brfss/annual_data/annual_2022.html | 445,132 | 445,132 (all) | multiset match 1.0; row order equals the raw file; every cell equals a recode of the raw variable |
| heart_2022_no_nans | 2022 LLCP | 445,132 | 246,022 (0.5526) | complete cases of heart_2022_with_nans; multiset match 1.0 |

## Outcome: not the same across versions

| Version | Column | BRFSS source | Meaning |
|---|---|---|---|
| 2020 | HeartDisease | _MICHD | Myocardial infarction OR coronary heart disease/angina |
| 2022 | HadHeartAttack | CVDINFR4 | Myocardial infarction only |
| 2022 | HadAngina (a feature) | CVDCRHD4 | Coronary heart disease or angina |

- In 2020, 9,874 of 27,373 positives (0.3607) report no infarction (9,675 "no", 192 "don't know", 6 refused, 1 missing).
- In heart_2022_no_nans, HadAngina = Yes in 0.5040 of HadHeartAttack positives (6,772 / 13,435) and 0.0351 of negatives (8,181 / 232,587), Cohen's h 1.2015. HadAngina is a label-adjacent co-feature.
- Under the 2020 definition, heart_2022_no_nans would hold 21,616 positives, 8,181 (0.3784) of them negative for HadHeartAttack.
- Results on the 2020 and 2022 versions are therefore not comparable as "heart disease" results.

## Missing codes (2022)

- heart_2022_with_nans recodes "don't know" and refused to missing on every item, and recodes the valid answer "never had a routine checkup" (CHECKUP1 = 8, 2,509 respondents) to missing.
- Respondents with "don't know" on PNEUVAC4, TETANUS1, LCSCTSC1, HIVTST7 or COVIDPOS, or CHECKUP1 = 8: 89,232. Any "don't know" on the 32 source items: 124,631. Any "don't know" or refused: 167,259. None of these respondents is in heart_2022_no_nans.
- Of the 199,110 respondents excluded from heart_2022_no_nans, 98,073 are excluded only because of "don't know" answers.

## Race

- 2020 Race is the CDC-imputed _IMPRACE: 4,510 rows with reported race "don't know/refused" carry an imputed race (3,997 White). "Other" pools Native Hawaiian or other Pacific Islander (1,667), other race (2,326), multiracial (6,710) and 225 imputed rows.
- 2022 RaceEthnicityCategory is the non-imputed _RACEGR4: 14,057 respondents are missing on race (14,055 with _RACEGR4 = 9 and 2 with no race code) and none is in heart_2022_no_nans. "Other race only, Non-Hispanic" (12,205 rows in no_nans) pools Asian (6,813), American Indian or Alaska Native (3,895) and Native Hawaiian or other Pacific Islander (1,497).
- Subgroup or fairness analyses on these columns use imputed (2020) or pooled (2022) groups.

## Survey design and prevalence

- Not included in any version: _LLCPWT, _STSTR, _PSU.
- 2020 _MICHD: unweighted file rate 0.0855; weighted 0.0648 among valid respondents (SE 0.0008) and 0.0648 in the file population (SE 0.0009).
- 2022 infarction: unweighted file rate 0.0546; weighted 0.0441 among valid respondents (SE 0.0006) and 0.0429 in the complete-case population (SE 0.0007).

## Duplicates

heart_2020_cleaned has 18,078 exact duplicate rows (0.0565); heart_2022_with_nans 157; heart_2022_no_nans 9. The 2020 duplicates are reproduced by the rebuild and are distinct respondents.

## Recommended use

- Name the outcome by its source code (MI or CHD for 2020; MI only for 2022) and do not compare across versions without harmonising it.
- Consider excluding HadAngina when HadHeartAttack is the target, or report results with and without it.
- Keep "don't know" and "never" as categories instead of deleting respondents; prefer heart_2022_with_nans over heart_2022_no_nans.
- Use the design-complete rebuild for population quantities.

## File hashes (SHA-256)

| File | SHA-256 |
|---|---|
| heart_2020_cleaned.csv | 90a1e2e8bdcb4aba54314a41d35d2ac3be4763e459df33951e08e415f527f5a8 |
| heart_2022_with_nans.csv | 9c5be2d641c60b63d395cb374581e4a691dbfe3cf0258dc437535b79e7a30a79 |
| heart_2022_no_nans.csv | f5eddf47d85170f2f7bc3ba523c275d705ddf22518f95d50aa33ddcfd786a94f |

Proportions are truncated to four decimals.
