# Numbers of the presentation (opening, blocks A, B and C)

Written by `src/make_numbers.py` from `data/processed/cities.csv`, `clusters.csv` and the three
`classification*.csv` files of notebook 04: do not edit by hand, run the script again (after notebook 04).
Slide numbers follow the final deck (28 slides): opening and block A 1–10, block B 11–18, block C 19–27.
"backup" = not on a slide, ready for questions.
Block C scores are class-weighted model scores, not probabilities.

| Slide | What | Value | Source |
| --- | --- | --- | --- |
| 2 | Milan, days a year with PM10 above 50 | 50 | notebook 01 |
| 3 | Milan NO₂, mean 2016–2023 | 35.1 µg/m³, rank 1 of 284 | notebook 02, section 3; figure A0 |
| 3 | Milan PM10, mean 2016–2023 | 29.9 µg/m³, rank 21 of 284 | notebook 02, section 3; figure A0 |
| 3 | Cities with more PM10 than Milan, in the Po Valley or Poland | 16 of 20 (Po Valley 10, Poland 6) | notebook 02, section 6; figure A0 |
| 6 | Cities in the study | 284 | notebook 01, final table |
| 6 | Countries; Italian cities | 20; 57 | notebook 01 |
| 6 | Period; rule for a city to enter | 2016–2023; valid data in at least 6 of 8 years, background stations only | notebook 01 |
| 6 | Columns of the final table | 28 | notebook 01 |
| 8 | Cities with mean PM10 above 20 µg/m³ (reference: EU 2030 annual limit; background means, not compliance) | 112 of 284 | notebook 02, section 4; figure A1 |
| 8 | Cities above the WHO 2021 guideline for PM10 (15 µg/m³) | 223 of 284 | notebook 02, section 4; figure A1 |
| 9 | Milan's percentile, NO₂ | 100 | notebook 02, section 3; figure A5 |
| 9 | Milan's percentile, ozone peaks | 99 | notebook 02, section 3; figure A5 |
| 9 | Milan's percentile, PM10 | 93 | notebook 02, section 3; figure A5 |
| 9 | Milan's percentile, winter wind | 2 | notebook 02, section 3; figure A5 |
| 9 | Milan winter wind vs European median | 2.1 vs 4.5 m/s | notebook 02, section 3; figures A4, A5 |
| 9 | Cities with less winter wind than Milan | 2% | notebook 02, section 3 |
| 10 | Cities per group (Po Valley / Poland / rest) | 25 / 32 / 227 | src/groups.py; notebook 02, section 6 |
| 10 | Median PM10 (Po Valley / Poland / rest) | 29.2 / 25.9 / 17.1 µg/m³ | notebook 02, section 6; figure A6 |
| 10 | Median NO₂ (Po Valley / Poland / rest) | 24.4 / 16.7 / 16.4 µg/m³ | notebook 02, section 6; figure A6 |
| 10 | Median winter wind (Po Valley / Poland / rest) | 2.6 / 5.0 / 4.5 m/s | notebook 02, section 6; figure A6 |
| 12 | Cities without PM2.5 | 40 | notebook 02, section 2 |
| 12 | Milan PM10 winter/summer; NO₂ weekend decrease (Sat–Sun vs Mon–Fri) | 2.5 times; 16% lower | notebook 01; notebook 03, section 1 |
| 13 | Stability (median ARI, 100 resamples) at k = 2 / k = 4 | 0.98 / 0.69 | notebook 03, section 4; figure B1 |
| 13 | Stability for k = 3–6 and k = 7–8 | 0.69–0.75 and 0.49 | notebook 03, section 4 |
| 13 | Silhouette at k = 2; range for k = 3–8 | 0.40; 0.20–0.22 | notebook 03, section 4 |
| 14 | Cluster sizes k = 2 (winter smog / rest) | 35 / 249 | notebook 03, section 5 |
| 14 | Winter-smog cluster: Po Valley / Polish / other cities | 25 (all of them) / 4 / 6 | notebook 03, section 5.5 |
| 15 | Cluster sizes k = 4 (stagnant / particle / moderate / clean) | 27 / 42 / 126 / 89 | notebook 03, section 5 |
| 15 | Mean PM10, stagnant vs particle smog | 28 vs 27 µg/m³ | notebook 03, section 5.2; figure B2 |
| 15 | Mean NO₂, stagnant vs particle smog | 25 vs 19 µg/m³ | notebook 03, section 5.2; figure B2 |
| 15 | NO₂ winter/summer, stagnant vs particle smog | 2.63 vs 1.66 | notebook 03, section 5.2; figure B2 |
| 16 | Particle-smog cluster: Polish cities | 25 of 42 | notebook 03, section 5.5 |
| 16 | Mean-shift: clusters found; agreement with k-means k = 2 (ARI) | 2 for every bandwidth; 0.96–0.98 | notebook 03, section 6 |
| 16 | Resamples in which all 35 winter-smog cities stay together | 81 of 100 | notebook 03, section 4.3 |
| 16 | With PM2.5 (244 cities): polluted cluster size; core kept; Polish cities in it | 60; 32 of 32; 21 | notebook 03, section 8 |
| 17 | Median winter wind by cluster (stagnant / particle / moderate / clean) | 2.4 / 4.8 / 4.7 / 4.4 m/s | notebook 03, section 7; figure B4 |
| 17 | Effect size ε² of winter wind, k = 2 / k = 4 | 0.18 / 0.22 | notebook 03, section 7; figure B4 |
| 17 | Effect size ε² of population, k = 2 / k = 4 | 0.00 / 0.01 | notebook 03, section 7 |
| 17 | Particle smog: median winter temperature; frost days; distance from sea | 0.8 °C; 105 days; 321 km | notebook 03, section 7 |
| 18 | Milan's rank on PC1 (general pollution level) | 1 of 284 | notebook 03, section 9; figure B5 |
| 18 | Cities over the exceedance indicator, stagnant / particle / moderate / clean | 17 of 27 / 13 of 42 / 0 of 126 / 0 of 89 | notebook 03, section 7 |
| 20 | Cities over the PM10 exceedance indicator (> 35 days above 50 µg/m³, mean of background stations 2016–2023; not a legal check) | 30: Po Valley 17, Poland 8, other 5; Italian 19 | notebook 01 |
| 20 | Cities over the PM10 exceedance indicator | 30 of 284 (10.6%) | notebook 04, section 1 |
| 20 | 'Always no': accuracy; AUC; average precision of a model with no skill | 0.894; 0.5; 0.106 | notebook 04, section 1 |
| 20 | Class weights: one city over the limit counts as many cities under it as | 8.47 | notebook 04, section 1 |
| 20 | Cities over 35 observed days; if missing days are annualised (which cities cross) | 30; 32 (Kielce, Piacenza) | notebook 04, section 1 |
| 21 | Cities sharing all 10 weather values with another city (same NASA POWER cell) | 41 (20 groups; e.g. Milano–Bergamo, Katowice–Zabrze) | notebook 04, sections 3 and 7 |
| 22 | Random forest, weather only: AUC random / geographic [95% interval] | 0.90 / 0.87 [0.69–0.94] | notebook 04, section 5; figure C1 |
| 22 | Random forest, weather only: average precision, geographic (no skill = 0.106) | 0.39 | notebook 04, section 5 |
| 22 | Logistic regression, weather: AUC random / geographic [95% interval] | 0.76 / 0.67 [0.30–0.86] | notebook 04, section 5; figure C1 |
| 22 | Lowest geographic AUC of all 6 models | 0.63 [0.27–0.81] (Logistic regression, M3 + population) | notebook 04, section 5 |
| 22 | Random forest with population: geographic AUC; difference from weather only (paired bootstrap) | 0.83 [0.65–0.92]; 0.04 [0.00–0.07] | notebook 04, section 5 |
| 22, 24 | At score ≥ 0.5: found / missed / false alarms; precision | 17 / 13 / 20; 17/37 = 0.46 | notebook 04, section 5 |
| 22 | Scores are not probabilities: mean score vs real share over the limit | 0.17 vs 0.11 | notebook 04, section 5 |
| 23 | Drop in AUC, families shuffled together: wind / temperature family / humidity (median) | 0.20 / 0.11 / 0.014 | notebook 04, section 6; figure C2 |
| 23 | Drop in AUC, one at a time: yearly wind / winter wind (median) | 0.057 / 0.029 | notebook 04, section 6 |
| 23 | Not drawn (no loss): Day–night range, Rain (log), Solar radiation (median drop in AUC) | -0.005 / 0.000 / -0.002 | notebook 04, section 6; caption of figure C2 |
| 24 | Cities over the limit flagged (score ≥ 0.5), forest weather only, geographic | 17 of 30 | notebook 04, section 5 |
| 24 | Po Valley cities over the limit flagged; Polish ones flagged (geographic CV) | 16 of 17; 0 of 8 | notebook 04, section 7; figure C3 |
| 24 | Po Valley cities just above the threshold | Modena 0.52, Carpi 0.51, Parma 0.51 | notebook 04, section 7 |
| 24 | Polish cities over vs under the limit: median winter wind; winter temperature | 4.9 vs 5.0 m/s; 0.4 vs 0.6 °C | notebook 04, section 7 |
| 24 | AUC among the 32 Polish cities only | 0.46 | notebook 04, section 7 |
| 24 | False alarms; of them Italian | 20; 15 | notebook 04, section 7 |
| 24 | Kraków: score random / geographic | 0.30 / 0.16 | notebook 04, section 7 |
| 25 | AUC, random: weather / latitude and longitude only | 0.90 / 0.83 | notebook 04, section 7; figure C4 |
| 25 | AUC, 12 geographic blocks: weather / latitude and longitude only | 0.87 / 0.77 | notebook 04, section 7; figure C4 |
| 25 | AUC, one country left out: weather / latitude and longitude only | 0.65 / 0.45 | notebook 04, section 7; figure C4 |
| 25 | Po Valley cities over the limit flagged — 12 blocks: Italian block hidden (Torino in training) | 16 of 16 | notebook 04, section 7; figure C4 |
| 25 | Po Valley cities over the limit flagged — same, Torino removed from training | 3 of 16 | notebook 04, section 7; figure C4 |
| 25 | Po Valley cities over the limit flagged — all 25 Po Valley cities hidden (Terni, Napoli in training) | 13 of 17 | notebook 04, section 7; figure C4 |
| 25 | Po Valley cities over the limit flagged — all 57 Italian cities hidden | 2 of 17 | notebook 04, section 7; figure C4 |
| 26 | Cluster stagnant winter smog: cities over the limit flagged | 16 of 17 | notebook 04, section 8; figure C5 |
| 26 | Cluster cold-winter particle smog: cities over the limit flagged | 1 of 13 | notebook 04, section 8; figure C5 |
| 26 | Milan: score random / geographic; rank in its cluster; cluster median | 0.95 / 0.59; 8–9 (tied) of 27; 0.58 | notebook 04, section 8; figure C5 |
| backup | Spearman winter wind vs PM10: all / Italy / Poland | -0.16 / -0.44 / -0.54 | notebook 02, section 5; figure A2 |
| backup | Strongest weather correlation with PM10 (all cities) | humidity -0.43 | notebook 02, section 5; figure A2 |
| backup | Yearly mixing layer vs humidity (why it was dropped) | -0.62 | notebook 02, section 5 |
