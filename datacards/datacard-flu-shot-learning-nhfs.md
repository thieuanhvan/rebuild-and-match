# Corrected Data Card: Flu Shot Learning (National 2009 H1N1 Flu Survey)

Applies to: DrivenData competition Flu Shot Learning: Predict H1N1 and Seasonal Flu Vaccines (https://www.drivendata.org/competitions/66/flu-shot-learning/page/211/) and its Kaggle copy (https://www.kaggle.com/datasets/jeromeblanchet/flu-shot-learning-h1n1-seasonal-flu-vaccines, version 1): training_set_features.csv, training_set_labels.csv, test_set_features.csv.

Source: National 2009 H1N1 Flu Survey (NHFS) public-use file, https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/nis/nhfs/. The NHFS was conducted by the CDC (NCHS and NCIRD); the analyses and interpretations here are the author's and not those of the CDC.

## Source and rebuild

| Item | Count |
|---|---|
| NHFS interview records | 70,944 (56,656 adults, 14,288 children) |
| Published rows | 53,415 (training 26,707, test 26,708) |
| Published rows matched by rebuilt adults | 53,415 (multiset match 1.0 on the 32 unscrambled columns) |
| Training rows matched including both labels | 26,707 of 26,707 |
| Adults absent from the published files | 3,241 (0.0572 of adults) |
| Absent adults whose feature tuple never occurs in the files | 3,238 |

- Children are not in the files. No documented rule explains the 3,241 absent adults; they are spread over all nine interview months, both phone samples and all age groups. Within repeated tuples, the split of absent adults between a missing and a present label is not identified (429 or 430 with a missing label).
- A second, independently written set of scripts reproduced these counts.

## Labels

- h1n1_vaccine and seasonal_vaccine come from VACC_H1N1_F and VACC_SEAS_F: vaccination status at the time of the interview.
- The interview month (INT_MONTH) is not in the files. In the linked training rows, the H1N1 share is 0.0190 in October 2009 and 0.3121 in June 2010; the seasonal share is 0.3573 in October and between 0.4293 and 0.5045 later. "Not vaccinated" therefore refers to different points of the campaign.

## Recodes

- Opinion items (raw 01–04, 77 don't know): published 1–5 with 04 as 1, 03 as 2, 77 as 3, 02 as 4, 01 as 5; refused becomes missing. The problem description states that "don't know" is placed at the scale midpoint.
- household_adults = N_ADULT_R − 1 (published range 0–3).
- doctor_recc_*: a recommendation of both vaccines counts as 1 for each.
- hhs_geo_region, employment_industry and employment_occupation are random strings, applied consistently: each NHFS code (10 regions, 21 industries, 23 occupations) maps to one string; industry and occupation codes 97, 98 and blank become missing.

## Missing values that mean "not asked"

- health_insurance is missing for all respondents interviewed from October to December 2009, 0.7508 in January 2010 and between 0.0516 and 0.0787 later, consistent with the item being added during fieldwork.
- doctor_recc_h1n1 is missing for 0.4562 of October respondents.
- These values are recorded as missing, with no distinction from non-response; their pattern predicts an early interview (AUC 0.9133).

## Survey design and prevalence

- Not included: the final weight FLUWT and other design variables.
- H1N1 vaccination: unweighted 0.2124 in the training rows; weighted 0.1927 among adults with a valid answer and 0.1918 in the file population.
- Seasonal vaccination: unweighted 0.4656 in the training rows; weighted 0.3922 and 0.3916.

## Recommended use

- Restore the interview month from the NHFS file when the label is used as a vaccination outcome, or restrict comparisons to respondents interviewed at the same time.
- Treat missing health_insurance and doctor_recc values before 2010 as "not asked".
- Use weighted estimates from the NHFS file for population quantities.

## File hashes (SHA-256, Kaggle copy)

| File | SHA-256 |
|---|---|
| training_set_features.csv | 9a805f24b45fd9bd0b52cedf7cab0ccc62b512372f00151b028b004b0973d1e5 |
| training_set_labels.csv | 0ad33a821b96666a0dbfafc4e6fe23969ded212c6b55eb8763bd8bd78b8cae40 |
| test_set_features.csv | fbb8e4f208c222a1559c701dd351e5db8fc12c1671393a009bdc055830fa42b5 |
| nhfspuf.dat (NHFS source) | f6c0890bbeae08861966498cffb32c78202059dcf9b929d7e8c063330120f7b4 |

Proportions are truncated to four decimals.
