# Corrected Data Card: Cardiovascular Diseases Risk Prediction Dataset (BRFSS 2021)

Applies to: Kaggle dataset Cardiovascular Diseases Risk Prediction Dataset (https://www.kaggle.com/datasets/alphiree/cardiovascular-diseases-risk-prediction-dataset), file CVD_cleaned.csv.

## Source and rebuild

| File | BRFSS source | Raw respondents | Rows (share) | Rebuild |
|---|---|---|---|---|
| CVD_cleaned | 2021 LLCP, https://www.cdc.gov/brfss/annual_data/annual_2021.html | 438,693 | 308,854 (0.7040) | multiset match 1.0; one rule per column followed by four undocumented steps; the 80 exact duplicate rows are reproduced |

## Outcome and variables

- Heart_Disease is the CDC-calculated _MICHD (myocardial infarction or coronary heart disease), as documented.
- Sex is the CDC-calculated _SEX, not the reported SEXVAR.

## Food items: sequential conversion

- BRFSS records each food item as one code that combines a unit and a count (1xx per day, 2xx per week, 3xx per month, 300 less than once a month).
- The file is reproduced only if the conversions are applied in sequence to the same column: 300 is set to missing; 101–199 becomes (value − 100) × 30; 201–299, including results of the first step, becomes (value − 200) × 4; 300–399, again including earlier results, loses 300.
- Seven times a day (code 107) becomes 40 a month, where a direct conversion gives 210; ten times a day (110) becomes 0.
- 1,666 rows (0.0053) carry at least one value produced by the sequential conversion (fruit 1,055; green vegetables 738; fried potatoes 150).

## Exclusions not in the documentation

Of the 336,651 respondents complete on the 19 columns under the direct conversion, 27,797 (0.0825) are absent from the file. Counted in order:

| Step | Respondents |
|---|---|
| "Less than once a month" on a food item set to missing, then deleted | 15,097 |
| Converted food value above 128 | 5,101 |
| No valid answer on days of poor physical or mental health (items not in the file) | 7,599 |

The excluded respondents are older and less healthy than those kept: heart disease 0.1092 against 0.0808, age 80 or over 0.1287 against 0.0721, fair or poor general health 0.2412 against 0.1526.

## Survey design and prevalence

- Not included: _LLCPWT, _STSTR, _PSU.
- _MICHD: unweighted file rate 0.0808; weighted 0.0613 (SE 0.0007) among the 434,058 respondents with a valid answer and 0.0611 (SE 0.0008) in the file population.

## Recommended use

- Treat the food columns as capped, sequentially converted values, not as servings per month; rebuild them with a direct conversion if per-serving associations matter.
- Treat the file as a selected subsample (complete cases, cap at 128, valid poor-health days).
- Use the design-complete rebuild for population quantities.

## File hashes (SHA-256)

| File | SHA-256 |
|---|---|
| CVD_cleaned.csv | 0c3c399c95c9df8ba65fa36821a95c8f27609508dc6927b6a6e7034f25a492c8 |

Proportions are truncated to four decimals.
