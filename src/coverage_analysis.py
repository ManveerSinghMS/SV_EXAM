"""Year-by-year coverage per city (2016-2023) and per-city means.

Rules:
- a station-year is valid if it has at least 75% of the days (>= 274) for PM10/PM2.5,
  or yearly coverage >= 0.75 for NO2/O3 (rows of coverage_no2_o3_station_years.csv are already filtered);
- a city-year is valid for a pollutant if it has at least one valid background station.

Usage (from the repository root):
    python3 src/coverage_analysis.py
Reads data/interim/coverage_pm_station_years.csv, data/interim/coverage_no2_o3_station_years.csv,
data/catalog/catalog_cities.csv; writes data/interim/coverage_cities_2016_2023.csv
"""
import pandas as pd

YEARS = list(range(2016, 2024))
pm = pd.read_csv("data/interim/coverage_pm_station_years.csv")
pm_ok = pm[pm.year.isin(YEARS) & (pm.valid_days >= 274)]
no = pd.read_csv("data/interim/coverage_no2_o3_station_years.csv")
no = no[no.year.isin(YEARS)]
cities = pd.read_csv("data/catalog/catalog_cities.csv")

# number of valid years per city and pollutant
years_ok = {}
for pol, df in [("PM10", pm_ok[pm_ok.pollutant == "PM10"]), ("PM2.5", pm_ok[pm_ok.pollutant == "PM2.5"]),
                ("NO2", no[no.pollutant == "NO2"]), ("O3", no[no.pollutant == "O3"])]:
    years_ok[pol] = df.groupby(["country", "city"]).year.nunique()
cov = pd.DataFrame(years_ok).fillna(0).astype(int).reset_index()
cov.columns = ["country", "city", "years_PM10", "years_PM25", "years_NO2", "years_O3"]

# per-city means: mean of the valid background stations in each year, then mean over the years
pm10 = pm_ok[pm_ok.pollutant == "PM10"].groupby(["country", "city", "year"]).agg(
    pm10=("mean", "mean"), above50=("days_above_50", "mean")).reset_index()
pm10_c = pm10.groupby(["country", "city"]).agg(pm10_mean=("pm10", "mean"), days_above_50=("above50", "mean")).reset_index()
pm25 = pm_ok[pm_ok.pollutant == "PM2.5"].groupby(["country", "city", "year"])["mean"].mean().groupby(["country", "city"]).mean().rename("pm25_mean").reset_index()
no2 = no[no.pollutant == "NO2"].groupby(["country", "city", "year"]).value.mean().groupby(["country", "city"]).mean().rename("no2_mean").reset_index()
o3 = no[no.pollutant == "O3"].groupby(["country", "city", "year"]).value.mean().groupby(["country", "city"]).mean().rename("o3_p93_max8h").reset_index()

out = cities[["country", "city", "lat", "lon", "altitude"]].merge(cov, on=["country", "city"], how="left").fillna(
    {c: 0 for c in ["years_PM10", "years_PM25", "years_NO2", "years_O3"]})
for t in [pm10_c, pm25, no2, o3]:
    out = out.merge(t, on=["country", "city"], how="left")
for k in [5, 6, 7]:
    out[f"ok_{k}years"] = (out.years_PM10 >= k) & (out.years_NO2 >= k) & (out.years_O3 >= k)
out = out.round(2).sort_values(["country", "city"])
out.to_csv("data/interim/coverage_cities_2016_2023.csv", index=False)

print("Cities with valid PM10+NO2+O3 in at least k of 8 years (2016-2023):")
for k in [8, 7, 6, 5, 4]:
    m = (out.years_PM10 >= k) & (out.years_NO2 >= k) & (out.years_O3 >= k)
    print(f"  k={k}: {m.sum()} cities, {out[m].country.nunique()} countries; also with PM2.5: {(m & (out.years_PM25 >= k)).sum()}")
r = out[out.ok_6years].sort_values("pm10_mean", ascending=False).reset_index(drop=True)
r.index += 1
print("PM10 ranking (k=6), top 25:")
print(r[["country", "city", "pm10_mean", "days_above_50", "no2_mean"]].head(25).to_string())
print("Milan's position:", r.index[r.city == "Milano (greater city)"].tolist(), "of", len(r))
