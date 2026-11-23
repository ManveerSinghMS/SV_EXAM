""""Signature" variables for NO2, per background station and year (2016-2023):
winter mean (November-February), summer mean (May-August), weekday mean and weekend mean.
Sources: for Italy the E1a hourly data (daily mean with at least 18 hours), for the other countries
the daily values of the Zenodo version (days with daily coverage >= 0.75).
Only station-years already valid in coverage_no2_o3_station_years.csv are kept.

Usage: python3 signature_no2.py <zenodo_daily.parquet> <e1a_italy_zip_folder> <catalog_stations.csv>
                                <coverage_no2_o3_station_years.csv> <output.csv>
Output: data/interim/signature_no2_station_years.csv
"""
import sys, os, zipfile, tempfile, time
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import minipq

daily_z, folder_it, catalog, coverage, out = sys.argv[1:6]
valid = pd.read_csv(coverage)
valid = valid[(valid.pollutant == "NO2") & valid.year.between(2016, 2023)]
keys_z = set(zip(valid[valid.source == "Zenodo"].eoi, valid[valid.source == "Zenodo"].year))
keys_it = set(zip(valid[valid.source == "E1a"].eoi, valid[valid.source == "E1a"].year))
info = valid.drop_duplicates("eoi").set_index("eoi")[["country", "city"]]


def row(eoi, year, s):
    """s: daily series indexed by date."""
    m, wd = s.index.month, s.index.dayofweek
    return dict(country=info.loc[eoi, "country"], city=info.loc[eoi, "city"], pollutant="NO2", eoi=eoi, year=year,
                mean=s.mean(), mean_winter=s[m.isin([11, 12, 1, 2])].mean(), mean_summer=s[m.isin([5, 6, 7, 8])].mean(),
                mean_weekdays=s[wd < 5].mean(), mean_weekend=s[wd >= 5].mean())


t0 = time.time()
rows = []
# 1) other countries: Zenodo daily values, read one row group at a time (the file is 200 MB)
eoi_z = {e for e, _ in keys_z}
parts = []
for z in minipq.iter_pandas(daily_z, ["Air.Quality.Station.EoI.Code", "year", "doy", "NO2", "cov.day.NO2"]):
    z.columns = ["eoi", "year", "doy", "NO2", "cov"]
    z = z[z.eoi.isin(eoi_z) & z.NO2.notna()]
    z = z[z["cov"].astype(float) >= 0.75]
    z["year"] = z.year.astype(int)
    parts.append(z[[k in keys_z for k in zip(z.eoi, z.year)]])
z = pd.concat(parts)
z["date"] = pd.to_datetime(z.year.astype(str) + "-01-01") + pd.to_timedelta(z.doy.astype(int) - 1, unit="D")
for (eoi, year), g in z.groupby(["eoi", "year"]):
    rows.append(row(eoi, year, g.set_index("date").NO2))
print("Zenodo:", len(rows), "station-years", round(time.time() - t0), "s", flush=True)

# 2) Italy: E1a hourly data
cat = pd.read_csv(catalog)
file2eoi = dict(zip(cat[cat.pollutant == "NO2"].file_e1a, cat[cat.pollutant == "NO2"].eoi))
series = {}
for zf in sorted(f for f in os.listdir(folder_it) if "_NO2_" in f):
    zz = zipfile.ZipFile(os.path.join(folder_it, zf))
    for it in zz.infolist():
        eoi = file2eoi.get(it.filename.split("/")[-1])
        if eoi is None or eoi not in info.index:
            continue
        with tempfile.TemporaryDirectory() as tmpdir:   # a folder, not NamedTemporaryFile: Windows cannot reopen an open temp file
            path = os.path.join(tmpdir, "data.parquet")
            with open(path, "wb") as parquet_file:
                parquet_file.write(zz.read(it))
            d = minipq.to_pandas(path, ["Start", "Value", "AggType", "Validity"])
        d = d[(d.AggType == "hour") & (d.Validity > 0) & d.Value.notna() & (d.Value >= 0)]
        series.setdefault(eoi, []).append(d[["Start", "Value"]])
for eoi, chunks in series.items():
    d = pd.concat(chunks).drop_duplicates("Start")
    d["day"] = d.Start.dt.floor("D")
    g = d.groupby("day").Value.agg(["mean", "count"])
    s = g[g["count"] >= 18]["mean"]
    for year, sy in s.groupby(s.index.year):
        if (eoi, year) in keys_it:
            rows.append(row(eoi, year, sy))
pd.DataFrame(rows).to_csv(out, index=False)
print("DONE", len(rows), "station-years", round(time.time() - t0), "s")
