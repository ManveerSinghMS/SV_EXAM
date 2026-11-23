"""Same statistics as coverage_pm.py for the countries whose E1a zip contains a single combined
data.parquet instead of one file per sampling point (Belgium, United Kingdom, Romania).
Rows are appended to the same output file.

Usage: python3 coverage_pm_combined_files.py <zip_folder> <catalog_stations.csv> <output.csv>
"""
import sys, os, re, zipfile, tempfile
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import minipq

folder, catalog, out = sys.argv[1:4]
cat = pd.read_csv(catalog)
background = cat[(cat.station_type == "background") & cat.area.isin(["urban", "suburban"]) & cat.pollutant.isin(["PM10", "PM2.5"])].copy()
key = lambda s: re.sub(r"[^A-Za-z0-9]", "", s).upper()   # sampling point names are written differently in the two sources
background["k"] = background.file_e1a.str.replace(r"\.parquet$", "", regex=True).map(key)
info = {r.k: r for r in background.itertuples()}
rows = []
for f in ["PM10_BE", "PM10_GB", "PM10_RO", "PM25_BE", "PM25_GB", "PM25_RO"]:
    z = zipfile.ZipFile(os.path.join(folder, f"eea_e1a_{f}.zip")); it = z.infolist()[0]
    with tempfile.TemporaryDirectory() as tmpdir:   # a folder, not NamedTemporaryFile: Windows cannot reopen an open temp file
        path = os.path.join(tmpdir, "data.parquet")
        with open(path, "wb") as parquet_file:
            parquet_file.write(z.read(it))
        d = minipq.to_pandas(path, ["Samplingpoint", "Start", "Value", "AggType", "Validity"])
    d = d[(d.Validity > 0) & d.Value.notna() & (d.Value >= 0)]
    d["k"] = d.Samplingpoint.str.split("/").str[-1].map(key)
    d = d[d.k.isin(info)]
    d["day"] = d.Start.dt.floor("D")
    for k, g0 in d.groupby("k"):
        g = g0[g0.AggType == "day"].groupby("day").Value.mean()
        h = g0[g0.AggType == "hour"].groupby("day").Value.agg(["mean", "count"]); h = h[h["count"] >= 18]["mean"]
        daily = pd.concat([g, h[~h.index.isin(g.index)]])
        r = info[k]
        for year, s in daily.groupby(daily.index.year):
            rows.append(dict(country=r.country, city=r.city, pollutant=r.pollutant, eoi=r.eoi, file_e1a=r.file_e1a, year=year,
                             valid_days=len(s), mean=round(s.mean(), 2), days_above_50=int((s > 50).sum())))
    print(f, d.k.nunique(), "background sampling points", flush=True)
pd.DataFrame(rows).to_csv(out, mode="a", header=not os.path.exists(out), index=False)
