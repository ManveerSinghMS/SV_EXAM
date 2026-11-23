# src

Shared code: helpers imported by the notebooks, the script that writes the numbers of the slides, and the scripts that built `data/interim/` from the raw data.

## Used by the notebooks

In a notebook: `import sys; sys.path.append("../src")`, then import what you need.

| File | What it does |
| --- | --- |
| `style.py` | Colours and style of every figure: cluster and area colours, map colours, colour scales, `apply_style()`, `show()` for tables, `source()` for the source line under a figure |
| `groups.py` | Shared definitions: `add_groups()` adds the Po Valley rule and the three areas (Po Valley, Poland, rest of Europe); `add_logs()` adds the logarithms of the skewed variables |
| `maps.py` | Maps of Europe without extra libraries: `draw_europe()` draws land, sea and borders in the EEA equal-area projection; `to_map()` turns longitude and latitude into map coordinates |
| `validation.py` | Geographic cross-validation shared by blocks B and C: `spatial_blocks()` splits the cities into 12 geographic blocks; `compare_cv()` scores a model with random and geographic cross-validation side by side; `out_of_fold()` returns the predictions for unseen blocks |

## Numbers of the slides

| File | What it does | Writes |
| --- | --- | --- |
| `make_numbers.py` | Recomputes every number of the slides from `data/processed/`. Run `python src/make_numbers.py` from the repository root | `slides/NUMBERS.md` |

## Data scripts (need the raw data, see `data/README.md`)

Run from the repository root; each script says its inputs at the top.

| File | What it does | Writes |
| --- | --- | --- |
| `coverage_pm.py` | PM10 and PM2.5 per background station and year: valid days, mean, days above 50 µg/m³ | `coverage_pm_station_years.csv` |
| `coverage_pm_combined_files.py` | The same for Belgium, United Kingdom and Romania, whose files have a different layout | appends to the same file |
| `coverage_no2_o3_e1a.py` | NO₂ yearly mean and ozone peaks per Italian background station and year | `coverage_no2_o3_e1a_italy.csv` |
| `coverage_analysis.py` | Valid years and means per city; marks the cities with at least 6 valid years out of 8 | `coverage_cities_2016_2023.csv` |
| `signature_pm.py` | PM10 and PM2.5 per station and year: winter, summer, weekday and weekend means | `signature_pm_station_years.csv` |
| `signature_no2.py` | The same for NO₂ | `signature_no2_station_years.csv` |
| `minipq.py` | Small Parquet reader used by the data scripts, so that they run without extra libraries | — |
