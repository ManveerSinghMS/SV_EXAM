"""Yearly statistics for every urban/suburban background sampling point of PM10 and PM2.5,
computed from the EEA validated E1a files: valid days, mean, days above 50 µg/m³ (PM10).

A daily value is the 'day' record when present, otherwise the mean of the hourly records
of that day (at least 18 valid hours).

Usage: python3 coverage_pm.py <zip_folder> <catalog_stations.csv> <output.csv>
Output: data/interim/coverage_pm_station_years.csv
"""
import sys, os, zipfile, tempfile, time
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import minipq

folder, catalog, out = sys.argv[1:4]
cat = pd.read_csv(catalog)
background = cat[(cat.station_type == "background") & cat.area.isin(["urban", "suburban"]) & cat.pollutant.isin(["PM10", "PM2.5"])]
info = {r.file_e1a: r for r in background.itertuples()}
done = set(pd.read_csv(out).file_e1a) if os.path.exists(out) else set()
rows, t0, n = [], time.time(), 0
for zf in sorted(f for f in os.listdir(folder) if f.endswith(".zip")):
    z = zipfile.ZipFile(os.path.join(folder, zf))
    for it in z.infolist():
        base = it.filename.split("/")[-1]
        if base not in info or base in done:
            continue
        done.add(base)
        with tempfile.TemporaryDirectory() as tmpdir:   # a folder, not NamedTemporaryFile: Windows cannot reopen an open temp file
            path = os.path.join(tmpdir, "data.parquet")
            with open(path, "wb") as parquet_file:
                parquet_file.write(z.read(it))
            try:
                d = minipq.to_pandas(path, ["Start", "Value", "AggType", "Validity"])
            except Exception as e:
                print("ERROR", base, e, flush=True); continue
        d = d[(d.Validity > 0) & d.Value.notna() & (d.Value >= 0)]
        if d.empty:
            continue
        d["day"] = d.Start.dt.floor("D")
        daily_records = d[d.AggType == "day"].groupby("day").Value.mean()
        hourly = d[d.AggType == "hour"].groupby("day").Value.agg(["mean", "count"])
        hourly = hourly[hourly["count"] >= 18]["mean"]
        daily = pd.concat([daily_records, hourly[~hourly.index.isin(daily_records.index)]]).sort_index()
        r = info[base]
        for year, s in daily.groupby(daily.index.year):
            rows.append(dict(country=r.country, city=r.city, pollutant=r.pollutant, eoi=r.eoi, file_e1a=base, year=year,
                             valid_days=len(s), mean=round(s.mean(), 2), days_above_50=int((s > 50).sum())))
        n += 1
        if n % 100 == 0:
            print(n, "files", round(time.time() - t0), "s", flush=True)
            pd.DataFrame(rows).to_csv(out, mode="a", header=not os.path.exists(out), index=False); rows = []
pd.DataFrame(rows).to_csv(out, mode="a", header=not os.path.exists(out), index=False)
print("DONE", n, "files", round(time.time() - t0), "s", flush=True)
