# Milan among European cities: air quality 2016–2023

Exam project for **Scientific and Data Visualization**, Università degli Studi di Milano.
Group: Paolo Cosentino, Manveer Singh, Muskaan Chaudhary.

## Research question

How does Milan's pollution profile compare with those of other European cities, which groups of cities
emerge, and how far do weather and location explain which cities exceed our PM10 exceedance indicator?

We answer it in three blocks:

| Block | Question | Method |
| --- | --- | --- |
| A | How does Milan compare with the other cities? | exploration, maps, percentile ranks |
| B | Which groups of cities emerge from their pollution alone? | k-means and mean-shift, validated with weather and geography |
| C | Can weather and location predict which cities have too many bad-air days? | random forest and logistic regression; random and geographic cross-validation, stricter hold-out tests |

## Data in brief

- **284 cities in 20 countries**, 2016–2023, only urban and suburban **background stations** (away from traffic and industry), so that cities are comparable.
- One row per city: pollution levels, the "shape" of the pollution (winter/summer, weekend), weather, geography, population.
- **PM10 exceedance indicator** (target of block C): more than 35 days a year above 50 µg/m³, averaged over the city's background stations and over 2016–2023. 30 cities of 284. It is built for the comparison, not a legal compliance check.

| Source | What we take from it |
| --- | --- |
| European Environment Agency (EEA), validated E1a data | PM10 and PM2.5 for all cities; NO₂ and ozone for Italy |
| EEA station data on Zenodo (record 17085064, CC BY 4.0) | NO₂ and ozone for the other countries |
| NASA POWER (MERRA-2) | monthly weather at each city's coordinates (cells of about 50 km) |
| Natural Earth 1:50m | coastline (distance from the sea) and country borders for the maps |
| Eurostat urb_cpop1; Statistik Austria, INSEE | city population |

Details of every file and every column: [`data/README.md`](data/README.md).

## Repository structure

```
data/
  raw/           downloaded data (about 1 GB, not in the repository)
  catalog/       list of cities and stations
  external/      maps, regions, missing populations
  interim/       tables per station and year, monthly weather, geography
  processed/     final tables: cities.csv, clusters.csv, classification.csv (+ the numbers of block C)
notebooks/       01_processing → 02_exploration → 03_clustering → 04_classification
src/             shared code (style, groups, maps, validation) and the data scripts
figures/         final figures (A = block A, B = block B, C = block C)
slides/          the presentation.
```

## How to run it

```
pip install -r requirements.txt
```

Then run the notebooks in order: **01 → 02 → 03 → 04**. They start from the CSV files in `data/interim/`,
so the raw data are not needed. Notebook 01 writes `data/processed/cities.csv`, which the others read.

Tested with Python 3.13, pandas 3.0, numpy 2.5, scipy 1.18, scikit-learn 1.9.1 (fixed: the random forests
change with the version), matplotlib 3.11.

The scripts `src/coverage_*.py` and `src/signature_*.py` rebuilt `data/interim/` from the raw data; they need
the raw files (see `data/README.md`).

## Notebooks

| Notebook | What it does | Output |
| --- | --- | --- |
| `01_processing` | from the intermediate tables to one row per city | `cities.csv` (284 × 28) |
| `02_exploration` | block A: Milan against the other cities, maps, correlations, three areas (Po Valley, Poland, rest) | figures A0–A6 |
| `03_clustering` | block B: groups of cities by pollution signature, stability, robustness, external validation | `clusters.csv`, figures B1–B5 |
| `04_classification` | block C: weather and location vs the PM10 exceedance indicator; which weather the model needs; who it misses; how strict the test is; predictions by cluster | `classification.csv`, `classification_models.csv`, `classification_checks.csv`, figures C1–C5 |

## Main results

- Milan has the **highest NO₂** of the 284 cities and is **21st for PM10**; its winter wind is less than half the median city's (2.1 vs 4.5 m/s).
- From pollution alone, **two stable groups** emerge: 35 "winter smog" cities (all 25 Po Valley cities) and 249 others. With four groups, the polluted cities split into two profiles: stagnant winter smog (Po Valley) and cold-winter particle smog (mostly Poland).
- **Weather alone** ranks the cities over the indicator well, also on held-out geographic blocks (AUC 0.90 random, 0.87 geographic; 95% interval 0.69–0.94 when the 12 blocks are resampled). It finds 16 of 17 Po Valley cities and none of the 8 Polish ones: there the weather does not explain the exceedances. The geographic test is less strict than it looks: without Torino in training only 3 of 16 Po Valley cities are found, and with one whole country left out the AUC is 0.65 (latitude and longitude alone: 0.45).

## Decision log

The main choices and why. Each is explained in the notebook where it is applied.

**Data**
- Only urban and suburban background stations, so that the effect of the city is not confused with where the monitors are placed.
- A station counts for a year with at least 274 valid days (PM) or 75% coverage (NO₂, ozone); a city keeps a year if at least one station is valid; a city is kept with at least 6 valid years out of 8 for each pollutant.
- NO₂ and ozone for Italy from the official E1a data instead of Zenodo, which had gaps in the Po Valley (agreement on shared stations: r = 0.998 and 0.996).
- 5 cities outside continental Europe removed (tropical or subtropical climate): 289 → 284.
- Weather from NASA POWER monthly means, one request per city.
- 12 missing populations filled from official sources only (`data/external/population_missing_official.csv`).
- PM2.5 is missing in 40 cities because their stations do not measure it: not filled; block B clusters without PM2.5 and checks the result on the 244 complete cities.
- The mixing-layer depth from NASA POWER follows climate rather than stagnant air (yearly value: Spearman −0.62 with humidity): the yearly value is not used in the models, the winter value only as a weak variable of the random forest. Winter wind is the measure of stagnation.
- Counting each station once instead of each sampling point changes PM10 by at most 0.54 µg/m³ and no city's target: aggregation kept.

**Shared definitions** (`src/groups.py`, `src/style.py`)
- **Po Valley** = written rule, not a hand-made list: Italian cities in Piemonte, Lombardia, Emilia-Romagna or Veneto, below 300 m, not in an Alpine valley. 25 cities.
- Three descriptive areas (Po Valley, Poland, rest of Europe), used only to describe, never inside the clustering or the models.
- Logarithms for strongly skewed variables (population, rain, days above 50, PM10 winter/summer, altitude), because k-means, PCA and logistic regression use distances or straight lines.
- Spearman correlations, because several variables are skewed.
- Colour-blind-safe palettes; maps in the EEA equal-area projection with WHO and EU reference classes; purple–orange scale for correlations (no "good" or "bad" sign).

**Block B**
- Six pollution variables, standardised: PM10, NO₂, ozone peaks, PM10 and NO₂ winter/summer, NO₂ weekend decrease. No weather, no coordinates: they are used afterwards to check the groups.
- Rule for the number of groups written before looking: bootstrap stability first (100 resamples, ARI). k = 2 is the main result (stability 0.98, silhouette 0.40); k = 4 a finer, less stable description (0.69).
- Checks: mean-shift, Ward, adding PM2.5, counting stations once. The core of 35 cities survives all of them.
- External validation with Kruskal–Wallis, Benjamini–Hochberg correction and effect size ε².

**Block C**
- Predictors in three nested sets: weather; + location (altitude, distance from the sea); + population. Never latitude and longitude, pollution variables or clusters.
- Logistic regression keeps a variable only if its |Spearman| with the ones already kept is ≤ 0.7; in cross-validation the rule is learned on the training cities of each fold.
- Two models: random forest (the main model) and logistic regression (a simpler comparison). A depth-2 tree was tried and removed: no conclusion depended on it.
- Random and geographic cross-validation side by side (12 geographic blocks, `src/validation.py`); AUC with a 95% interval from a bootstrap over the 12 blocks (neighbouring cities are not independent; resampling single cities gave 0.81–0.92 instead of 0.69–0.94), average precision, balanced accuracy and recall; class weights balanced. Model outputs are scores that rank cities, not probabilities.
- Stricter tests of the geographic split: Torino removed from training, the whole Po Valley and the whole of Italy left out, one country at a time; a model on latitude and longitude only as a baseline.
- Importance by permutation on held-out folds, with twin variables shuffled together (both winds).

## Limits

- The block C target counts the PM10 days **observed** above 50 (station-years with at least 274 valid days, missing days not filled in). If the missing days were like the measured ones, 32 cities instead of 30 would be over the indicator (Piacenza, Kielce): two borderline labels depend on data availability.
- Weather is a model value on cells of about 50 km and monthly: nearby cities share it, and short winter inversions are not seen.
- The PM10 indicator uses background stations and 8-year means: it is not the legal check.
- Associations, not causes: sources (for example heating in Poland) are hypotheses.
