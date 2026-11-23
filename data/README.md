# Data

The table used by all the analyses is **`processed/cities.csv`**: one row per city. Everything else shows how it was built.

```
raw/  →  catalog/ + interim/  →  processed/
         (src/ scripts)          (notebook 01)
```

## Folders

### raw/ — downloaded data (not in the repository, about 1 GB)

| Source | Files | Where |
| --- | --- | --- |
| EEA validated E1a data | PM10 and PM2.5 for all countries, NO₂ and ozone for Italy: one Parquet file per sampling point, zipped by country and pollutant | EEA download service (eeadmz1-downloads-api) |
| EEA metadata | sampling points of each city, station type and area, coordinates | same service |
| EEA station data on Zenodo | yearly and daily NO₂ and ozone, station metadata | zenodo.org, record 17085064 |
| NASA POWER | monthly T2M, T2M_RANGE, PRECTOTCORR, WS10M, RH2M, PS, PBLTOP, ALLSKY_SFC_SW_DWN, FROST_DAYS | power.larc.nasa.gov, monthly point API |
| Natural Earth | 1:50m coastline and countries | naturalearthdata.com |
| Eurostat | city population (urb_cpop1) | ec.europa.eu/eurostat |

### catalog/

| File | Content |
| --- | --- |
| `catalog_stations.csv` | every sampling point (7,334): city, pollutant, station code and name, type, area, coordinates, altitude |
| `catalog_cities.csv` | 573 cities with background stations; `complete` = has background PM10, NO₂ and ozone (456 cities) |

### external/

| File | Content |
| --- | --- |
| `coastline_europe.geojson` | Natural Earth coastline cropped to Europe (distance from the sea, maps) |
| `countries_europe.geojson` | Natural Earth country borders (maps) |
| `italian_cities_regions.csv` | region of the 57 Italian cities and whether they lie in an Alpine valley (Po Valley rule) |
| `population_missing_official.csv` | the 12 populations missing in Eurostat, with year and official source |

### interim/ — one row per station and year, or per city

| File | Content | Made by |
| --- | --- | --- |
| `coverage_pm_station_years.csv` | PM10 and PM2.5 per station and year: valid days, mean, days above 50 µg/m³ | `src/coverage_pm.py`, `src/coverage_pm_combined_files.py` |
| `coverage_no2_o3_e1a_italy.csv` | NO₂ and ozone per Italian station and year, from E1a | `src/coverage_no2_o3_e1a.py` |
| `coverage_no2_o3_station_years.csv` | NO₂ and ozone per station and year, all countries (Italy from E1a, the others from Zenodo), only years with ≥ 75% coverage | Zenodo yearly file + the Italian file above |
| `coverage_cities_2016_2023.csv` | one row per city: valid years per pollutant, means, `ok_6years` | `src/coverage_analysis.py` |
| `signature_pm_station_years.csv` | PM10 and PM2.5 per station and year: mean, winter, summer, weekdays, weekend | `src/signature_pm.py` |
| `signature_no2_station_years.csv` | the same for NO₂ | `src/signature_no2.py` |
| `weather_cities_monthly.csv` | NASA POWER monthly weather, one row per city, year, month and variable | NASA POWER API |
| `geography_cities.csv` | distance from the sea and Eurostat population | Natural Earth + Eurostat |

### processed/ — final tables

| File | Content | Made by |
| --- | --- | --- |
| `cities.csv` | 284 cities × 28 columns (below) | notebook 01 |
| `clusters.csv` | area, clusters k = 2 and k = 4 with names, mean-shift, PC1 and PC2 | notebook 03 |
| `classification.csv` | scores of the weather-only random forest (`score_random`, `score_geographic`: they rank cities, they are not probabilities) and outcome per city | notebook 04 |
| `classification_models.csv` | AUC with 95% interval, average precision, balanced accuracy and recall of the six models | notebook 04 |
| `classification_checks.csv` | the other numbers of block C (importances, stress tests), read by `src/make_numbers.py` | notebook 04 |

## Columns of `cities.csv`

All values are means over 2016–2023. Winter = November–February, summer = May–August.

| Column | Meaning | Unit |
| --- | --- | --- |
| `country`, `city` | country code and EEA city name | — |
| `lat`, `lon`, `altitude` | mean position of the city's background stations | degrees, m |
| `pm10_mean`, `pm25_mean`, `no2_mean` | yearly mean concentration | µg/m³ |
| `o3_peaks` | ozone peaks: 93rd percentile of the daily maximum 8-hour mean, whole year | µg/m³ |
| `pm10_days_above_50` | days a year with daily PM10 above 50 µg/m³ | days |
| `pm10_winter_summer`, `no2_winter_summer` | winter mean / summer mean | ratio |
| `no2_weekend_drop` | how much lower NO₂ is on Saturday–Sunday than on Monday–Friday | % |
| `pm25_pm10_ratio` | share of PM10 that is fine particles | ratio |
| `temperature`, `temperature_winter` | air temperature at 2 m, year and winter | °C |
| `diurnal_range` | daily temperature range | °C |
| `rain_mm_day` | precipitation | mm/day |
| `wind`, `wind_winter` | wind at 10 m, year and winter | m/s |
| `humidity` | relative humidity | % |
| `solar_radiation` | solar radiation at the surface | MJ/m² per day |
| `frost_days_year` | frost days | days/year |
| `mixing_layer_m`, `mixing_layer_winter_m` | rough depth of the mixing layer, (PS − PBLTOP) × 10 × 8.5 | m |
| `dist_sea_km` | distance from the coastline | km |
| `population` | city population | inhabitants |
| `exceeds_pm10_limit` | PM10 exceedance indicator: `pm10_days_above_50` > 35 | True/False |

Missing values: `pm25_mean` and `pm25_pm10_ratio` in 40 cities, whose stations do not measure PM2.5.
