"""Yearly NO2 and ozone per background station from the EEA validated E1a hourly data (used for Italy).
Same definitions as the Zenodo version:
- NO2: yearly mean of the valid hourly values;
- O3: 93.15th percentile of the daily maxima of the 8-hour running mean
  (running mean valid with at least 6 of 8 hours, daily maximum valid with at least 18 running means).
A station-year is kept if valid hours are at least 75% of the hours in the year.

Usage: python3 coverage_no2_o3_e1a.py <zip_folder> <catalog_stations.csv> <output.csv>
Output: data/interim/coverage_no2_o3_e1a_italy.csv
"""
import sys, os, zipfile, tempfile, time
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import minipq

folder, catalog, out = sys.argv[1:4]
cat = pd.read_csv(catalog)
background = cat[(cat.station_type == "background") & cat.area.isin(["urban", "suburban"]) & cat.pollutant.isin(["NO2", "O3"])]
info = {r.file_e1a: r for r in background.itertuples()}
rows, t0, n = [], time.time(), 0
for zf in sorted(f for f in os.listdir(folder) if f.endswith(".zip") and ("_NO2_" in f or "_O3_" in f)):
    z = zipfile.ZipFile(os.path.join(folder, zf))
    for it in z.infolist():
        base = it.filename.split("/")[-1]
        if base not in info:
            continue
        with tempfile.TemporaryDirectory() as tmpdir:   # a folder, not NamedTemporaryFile: Windows cannot reopen an open temp file
            path = os.path.join(tmpdir, "data.parquet")
            with open(path, "wb") as parquet_file:
                parquet_file.write(z.read(it))
            d = minipq.to_pandas(path, ["Start", "Value", "AggType", "Validity"])
        d = d[(d.AggType == "hour") & (d.Validity > 0) & d.Value.notna() & (d.Value >= 0)]
        if d.empty:
            continue
        s = d.groupby("Start").Value.mean().sort_index()
        r = info[base]
        for year, sy in s.groupby(s.index.year):
            hours_in_year = 8784 if year % 4 == 0 else 8760
            cov = len(sy) / hours_in_year
            if cov < 0.75:
                continue
            if r.pollutant == "NO2":
                value = sy.mean()
            else:
                full = sy.asfreq("h")
                m8 = full.rolling(8, min_periods=6).mean()
                count = m8.groupby(m8.index.floor("D")).count()
                daily_max = m8.groupby(m8.index.floor("D")).max()[count >= 18]
                if len(daily_max) < 274:
                    continue
                value = np.percentile(daily_max.values, 93.15)
            rows.append(dict(eoi=r.eoi, value=value, pollutant=r.pollutant, country=r.country, city=r.city,
                             year=year, coverage=round(cov, 3), source="E1a"))
        n += 1
        if n % 25 == 0:
            print(n, "stations", round(time.time() - t0), "s", flush=True)
pd.DataFrame(rows).to_csv(out, index=False)
print("DONE", n, "stations,", len(rows), "station-years", round(time.time() - t0), "s")
