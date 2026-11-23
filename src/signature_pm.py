""""Signature" variables for PM10 and PM2.5 from the E1a daily/hourly data, per background station and year (2016-2023):
winter mean (November-February), summer mean (May-August), weekday mean and weekend mean.
Handles both zips with one file per sampling point and zips with a single data.parquet (BE, GB, RO).
Only station-years with at least 274 valid days are kept.

Usage: python3 signature_pm.py <zip_folder> <catalog_stations.csv> <output.csv>
Output: data/interim/signature_pm_station_years.csv
"""
import sys, os, re, zipfile, tempfile, time
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import minipq

folder, catalog, out = sys.argv[1:4]
cat = pd.read_csv(catalog)
background = cat[(cat.station_type == "background") & cat.area.isin(["urban", "suburban"]) & cat.pollutant.isin(["PM10", "PM2.5"])].copy()
key = lambda s: re.sub(r"[^A-Za-z0-9]", "", s).upper()
background["k"] = background.file_e1a.str.replace(r"\.parquet$", "", regex=True).map(key)
by_file = {r.file_e1a: r for r in background.itertuples()}
by_key = {r.k: r for r in background.itertuples()}


def daily_series(d):
    """Daily series: 'day' records when present, otherwise hourly mean with at least 18 valid hours."""
    d = d[(d.Validity > 0) & d.Value.notna() & (d.Value >= 0)].copy()
    d["day"] = d.Start.dt.floor("D")
    g = d[d.AggType == "day"].groupby("day").Value.mean()
    h = d[d.AggType == "hour"].groupby("day").Value.agg(["mean", "count"])
    h = h[h["count"] >= 18]["mean"]
    return pd.concat([g, h[~h.index.isin(g.index)]]).sort_index()


def station_rows(s, r):
    s = s[(s.index.year >= 2016) & (s.index.year <= 2023)]
    for year, sy in s.groupby(s.index.year):
        if len(sy) < 274:
            continue
        m, wd = sy.index.month, sy.index.dayofweek
        yield dict(country=r.country, city=r.city, pollutant=r.pollutant, eoi=r.eoi, year=year,
                   mean=sy.mean(), mean_winter=sy[m.isin([11, 12, 1, 2])].mean(),
                   mean_summer=sy[m.isin([5, 6, 7, 8])].mean(),
                   mean_weekdays=sy[wd < 5].mean(), mean_weekend=sy[wd >= 5].mean())


rows, t0, n = [], time.time(), 0
for zf in sorted(f for f in os.listdir(folder) if f.endswith(".zip")):
    z = zipfile.ZipFile(os.path.join(folder, zf))
    for it in z.infolist():
        base = it.filename.split("/")[-1]
        combined = base == "data.parquet"
        if not combined and base not in by_file:
            continue
        with tempfile.TemporaryDirectory() as tmpdir:   # a folder, not NamedTemporaryFile: Windows cannot reopen an open temp file
            path = os.path.join(tmpdir, "data.parquet")
            with open(path, "wb") as parquet_file:
                parquet_file.write(z.read(it))
            cols = ["Start", "Value", "AggType", "Validity"] + (["Samplingpoint"] if combined else [])
            d = minipq.to_pandas(path, cols)
        if combined:
            d["k"] = d.Samplingpoint.str.split("/").str[-1].map(key)
            for k, g in d[d.k.isin(by_key)].groupby("k"):
                rows.extend(station_rows(daily_series(g), by_key[k]))
                n += 1
        else:
            rows.extend(station_rows(daily_series(d), by_file[base]))
            n += 1
        if n % 200 == 0:
            print(n, "stations", round(time.time() - t0), "s", flush=True)
pd.DataFrame(rows).to_csv(out, index=False)
print("DONE", n, "stations,", len(rows), "station-years", round(time.time() - t0), "s")
