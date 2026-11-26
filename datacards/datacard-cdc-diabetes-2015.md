# Corrected Data Card: CDC Diabetes Health Indicators (BRFSS 2015)

Applies to: UCI Machine Learning Repository dataset 891, data.csv (https://doi.org/10.24432/C53919), and the Kaggle Diabetes Health Indicators Dataset (https://www.kaggle.com/datasets/alexteboul/diabetes-health-indicators-dataset) files diabetes_012_health_indicators_BRFSS2015.csv, diabetes_binary_health_indicators_BRFSS2015.csv and diabetes_binary_5050split_health_indicators_BRFSS2015.csv. This card corrects and extends the existing documentation; it does not replace the data. Licence of the files: CC0: Public Domain according to the Kaggle dataset page (read 25 November 2026); the UCI page for dataset 891 refers to the Kaggle dataset for licensing.

## Source

- Survey: CDC Behavioral Risk Factor Surveillance System (BRFSS), 2015 LLCP public-use file, https://www.cdc.gov/brfss/annual_data/annual_2015.html (the UCI record links the 2014 page; the data are from 2015).
- Raw respondents: 441,456. Respondents with a valid diabetes answer: 440,658.
- Rows in the file: 253,680 (0.5746 of raw respondents), the respondents complete on the label and all 21 features.
- Rebuild: the files are reproduced exactly from the raw file (multiset match 1.0 for the UCI file and the Kaggle binary and three-class files; the 50:50 file is contained in the binary file). The release script gives every recode rule. BMI is _BMI5/100 rounded half-to-even; half-up rounding does not reproduce the file.

## Label (by BRFSS source code DIABETE3)

| DIABETE3 code | Meaning | Rows in file | Diabetes_012 | Diabetes_binary and 50:50 |
|---|---|---|---|---|
| 1 | Told they have diabetes | 35,346 | 2 | 1 |
| 4 | Prediabetes or borderline diabetes | 4,631 | 1 | 0 |
| 2 | Diabetes only during pregnancy | 1,978 | 0 | 0 |
| 3 | No | 211,725 | 0 | 0 |
| 7, 9, missing | Don't know, refused, missing | 0 (dropped) | n/a | n/a |

Correction: class 1 of the binary and 50:50 files is diabetes only. It does not include prediabetes. Existing documentation that says "1 = prediabetes or diabetes" describes the intended construction; the creator's notebook code recodes prediabetes to 0, and the data follow the code. A label of "prediabetes or diabetes" would have 39,977 positives; the file has 35,346. The 50:50 file has 70,692 rows (35,346 per class).

Pregnancy-only diabetes in class 0 is a deliberate choice of the creator (Kaggle discussion thread 316625, https://www.kaggle.com/datasets/alexteboul/diabetes-health-indicators-dataset/discussion/316625).

## Features

21 features, all survey answers or CDC computed variables from survey answers. There are no laboratory values; descriptions mentioning 35 features or laboratory test results do not apply to this file. There is no race variable.

## Survey design

- Not included: final weight _LLCPWT, stratum _STSTR, primary sampling unit _PSU, state _STATE.
- Consequence: the class-1 rate of the file (0.1393, unweighted) is not a prevalence. The weighted prevalence of diagnosed diabetes among all valid respondents is 0.1050 (design SE 0.0008); in the complete-case population of the file it is 0.1228 (SE 0.0012). With prediabetes included, the weighted prevalence among all valid respondents is 0.1209 (SE 0.0009).
- The release script rebuilds the file with the design variables attached, for users who need population estimates.

## Duplicates

The binary file contains 24,206 exact duplicate rows (0.0954) and the three-class file 23,899. They are reproduced by the rebuild and are distinct respondents with identical answers; removing them removes valid respondents (see Kaggle discussion thread 323593, https://www.kaggle.com/datasets/alexteboul/diabetes-health-indicators-dataset/discussion/323593).

## Later survey years

The same 21 items are not all collected in later years. The 2022 file lacks _RFHYPE6, TOLDHI3 and _CHOLCH3 (high blood pressure, high cholesterol, cholesterol check) and the fruit and vegetable items; the 2023 file lacks the fruit and vegetable items. A same-definition update cannot be built for 2022 or 2023.

## Recommended use

- Report the file version and download date; check copies against the hashes below.
- Do not report the class-1 rate as a prevalence; use the design-complete rebuild for population quantities.
- State the label as "diagnosed diabetes (excluding prediabetes and pregnancy-only diabetes)".
- Treat the file as a complete-case subsample (0.5746 of respondents).

## File hashes (SHA-256)

| File | SHA-256 |
|---|---|
| UCI data.csv | 9f71fda9d4ae5f4878c99b9233b6a16accfa9a17c194116a6b78100540934964 |
| diabetes_012_health_indicators_BRFSS2015.csv | a971809d0786d2d7d7f6070f83dfe8af9d860ea33a79e0e2701c8a49f78f9861 |
| diabetes_binary_health_indicators_BRFSS2015.csv | 19f367e3e3350768f0c144c5d73ee5b355f67a57eaaa86ca7bd8aec594d8b1d0 |
| diabetes_binary_5050split_health_indicators_BRFSS2015.csv | 873128ba0264d66a8b09bb6158f21fd4bedc10459d1ed5ecad3b94167a9539b4 |

Kaggle files hashed from copies dated 8 November 2021; the archive does not state a Kaggle version number, so the copy is identified by the SHA-256 hashes below. Proportions are truncated to four decimals.
