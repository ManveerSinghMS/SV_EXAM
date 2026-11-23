"""Every number said or written in the slides of the opening and of blocks A, B and C, recomputed from the data.

Why: three people write slides, script and notes; with one file that recomputes the numbers from the CSV files,
a number in a slide can never disagree with the analysis, and every number can be traced to its source
when a question comes at the exam. If the data or a choice change, run this again and compare.

Run from the repository root:   python src/make_numbers.py
Output: slides/NUMBERS.md
Block C: the model scores need the forests of notebook 04, so they are read from the three files that notebook 04 writes
(classification.csv, classification_models.csv, classification_checks.csv): run notebook 04 first, then this script.
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, MeanShift, estimate_bandwidth
from sklearn.metrics import silhouette_score, adjusted_rand_score

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT, "src"))
from groups import add_groups, add_logs

cities = add_logs(add_groups(pd.read_csv(os.path.join(ROOT, "data", "processed", "cities.csv"))))
clusters = pd.read_csv(os.path.join(ROOT, "data", "processed", "clusters.csv"))
cities = cities.merge(clusters[["country", "city", "cluster_k2", "cluster_k4"]], on=["country", "city"])
milan = cities[cities["city"].str.startswith("Milano")].iloc[0]
NB01, NB02, NB03, NB04 = "notebook 01", "notebook 02", "notebook 03", "notebook 04"

rows = []          # (slide, what, value, source)
def add(slide, what, value, source):
    rows.append((slide, what, value, source))

def pct(var):
    """Milan's percentile (rank among the cities, as in figure A5)."""
    return cities[var].rank(pct=True)[milan.name] * 100

# ---------------------------------------------------------------------------------------------
# Opening and block A (slides 2-10 of the final deck)
# ---------------------------------------------------------------------------------------------
n = len(cities)
add(6, "Cities in the study", f"{n}", f"{NB01}, final table")
add(3, "Milan NO₂, mean 2016–2023", f"{milan['no2_mean']:.1f} µg/m³, rank {int((cities['no2_mean'] > milan['no2_mean']).sum()) + 1} of {n}", f"{NB02}, section 3; figure A0")
rank_pm10 = int((cities["pm10_mean"] > milan["pm10_mean"]).sum()) + 1
above = cities[cities["pm10_mean"] > milan["pm10_mean"]]
add(3, "Milan PM10, mean 2016–2023", f"{milan['pm10_mean']:.1f} µg/m³, rank {rank_pm10} of {n}", f"{NB02}, section 3; figure A0")
add(3, "Cities with more PM10 than Milan, in the Po Valley or Poland",
    f"{int((above['group'] != 'Rest of Europe').sum())} of {len(above)} "
    f"(Po Valley {int((above['group'] == 'Po Valley').sum())}, Poland {int((above['group'] == 'Poland').sum())})", f"{NB02}, section 6; figure A0")
add(6, "Countries; Italian cities", f"{cities['country'].nunique()}; {int((cities['country'] == 'IT').sum())}", NB01)
add(6, "Period; rule for a city to enter", "2016–2023; valid data in at least 6 of 8 years, background stations only", NB01)
add(6, "Columns of the final table", f"{pd.read_csv(os.path.join(ROOT, 'data', 'processed', 'cities.csv')).shape[1]}", NB01)

# ---------------------------------------------------------------------------------------------
# Block A
# ---------------------------------------------------------------------------------------------
add(8, "Cities with mean PM10 above 20 µg/m³ (reference: EU 2030 annual limit; background means, not compliance)", f"{int((cities['pm10_mean'] > 20).sum())} of {n}", f"{NB02}, section 4; figure A1")
add(8, "Cities above the WHO 2021 guideline for PM10 (15 µg/m³)", f"{int((cities['pm10_mean'] > 15).sum())} of {n}", f"{NB02}, section 4; figure A1")
for var, name in [("no2_mean", "NO₂"), ("o3_peaks", "ozone peaks"), ("pm10_mean", "PM10"), ("wind_winter", "winter wind")]:
    add(9, f"Milan's percentile, {name}", f"{pct(var):.0f}", f"{NB02}, section 3; figure A5")
add(9, "Milan winter wind vs European median", f"{milan['wind_winter']:.1f} vs {cities['wind_winter'].median():.1f} m/s", f"{NB02}, section 3; figures A4, A5")
add(9, "Cities with less winter wind than Milan", f"{(cities['wind_winter'] < milan['wind_winter']).mean() * 100:.0f}%", f"{NB02}, section 3")
counts = cities["group"].value_counts()
add(10, "Cities per group (Po Valley / Poland / rest)", f"{counts['Po Valley']} / {counts['Poland']} / {counts['Rest of Europe']}", "src/groups.py; notebook 02, section 6")
med = cities.groupby("group")[["pm10_mean", "no2_mean", "wind_winter"]].median()
for var, name, unit in [("pm10_mean", "PM10", "µg/m³"), ("no2_mean", "NO₂", "µg/m³"), ("wind_winter", "winter wind", "m/s")]:
    add(10, f"Median {name} (Po Valley / Poland / rest)",
        f"{med.loc['Po Valley', var]:.1f} / {med.loc['Poland', var]:.1f} / {med.loc['Rest of Europe', var]:.1f} {unit}", f"{NB02}, section 6; figure A6")
over = cities[cities["exceeds_pm10_limit"] == 1]
add(20, "Cities over the PM10 exceedance indicator (> 35 days above 50 µg/m³, mean of background stations 2016–2023; not a legal check)",
    f"{len(over)}: Po Valley {int((over['group'] == 'Po Valley').sum())}, Poland {int((over['group'] == 'Poland').sum())}, "
    f"other {int((over['group'] == 'Rest of Europe').sum())}; Italian {int((over['country'] == 'IT').sum())}", NB01)
add(2, "Milan, days a year with PM10 above 50", f"{milan['pm10_days_above_50']:.0f}", NB01)
rho = lambda t, a, b: stats.spearmanr(t[a], t[b]).statistic
add("backup", "Spearman winter wind vs PM10: all / Italy / Poland",
    f"{rho(cities, 'wind_winter', 'pm10_mean'):.2f} / {rho(cities[cities['country'] == 'IT'], 'wind_winter', 'pm10_mean'):.2f} / "
    f"{rho(cities[cities['country'] == 'PL'], 'wind_winter', 'pm10_mean'):.2f}", f"{NB02}, section 5; figure A2")
add("backup", "Strongest weather correlation with PM10 (all cities)", f"humidity {rho(cities, 'humidity', 'pm10_mean'):.2f}", f"{NB02}, section 5; figure A2")
add(12, "Cities without PM2.5", f"{int(cities['pm25_mean'].isna().sum())}", f"{NB02}, section 2")
add("backup", "Yearly mixing layer vs humidity (why it was dropped)", f"{rho(cities, 'mixing_layer_m', 'humidity'):.2f}", f"{NB02}, section 5")

# ---------------------------------------------------------------------------------------------
# Block B (slides 12-18): same variables, scaling and seeds as notebook 03
# ---------------------------------------------------------------------------------------------
FEATURES = ["pm10_mean", "no2_mean", "o3_peaks", "log_pm10_winter_summer", "no2_winter_summer", "no2_weekend_drop"]
X = StandardScaler().fit_transform(cities[FEATURES])
add(12, "Milan PM10 winter/summer; NO₂ weekend decrease (Sat–Sun vs Mon–Fri)", f"{milan['pm10_winter_summer']:.1f} times; {milan['no2_weekend_drop']:.0f}% lower", f"{NB01}; {NB03}, section 1")

rng = np.random.default_rng(0)          # notebook 03, section 4.1: one generator for k = 2..8, in this order
stability, silhouette = {}, {}
for k in range(2, 9):
    reference = KMeans(n_clusters=k, n_init=50, random_state=0).fit_predict(X)
    silhouette[k] = silhouette_score(X, reference)
    scores = []
    for b in range(100):
        sample = rng.integers(0, len(X), len(X))
        scores.append(adjusted_rand_score(reference, KMeans(n_clusters=k, n_init=10, random_state=b).fit(X[sample]).predict(X)))
    stability[k] = np.median(scores)
add(13, "Stability (median ARI, 100 resamples) at k = 2 / k = 4", f"{stability[2]:.2f} / {stability[4]:.2f}", f"{NB03}, section 4; figure B1")
add(13, "Stability for k = 3–6 and k = 7–8",
    f"{min(stability[k] for k in range(3, 7)):.2f}–{max(stability[k] for k in range(3, 7)):.2f} and {min(stability[7], stability[8]):.2f}–{max(stability[7], stability[8]):.2f}".replace("0.49–0.49", "0.49"), f"{NB03}, section 4")
add(13, "Silhouette at k = 2; range for k = 3–8", f"{silhouette[2]:.2f}; {min(list(silhouette.values())[1:]):.2f}–{max(list(silhouette.values())[1:]):.2f}", f"{NB03}, section 4")

size2, size4 = cities["cluster_k2"].value_counts().sort_index(), cities["cluster_k4"].value_counts().sort_index()
add(14, "Cluster sizes k = 2 (winter smog / rest)", f"{size2[1]} / {size2[2]}", f"{NB03}, section 5")
add(15, "Cluster sizes k = 4 (stagnant / particle / moderate / clean)", " / ".join(str(size4[c]) for c in range(1, 5)), f"{NB03}, section 5")
prof = cities.groupby("cluster_k4")[["pm10_mean", "no2_mean", "no2_winter_summer"]].mean()
add(15, "Mean PM10, stagnant vs particle smog", f"{prof.loc[1, 'pm10_mean']:.0f} vs {prof.loc[2, 'pm10_mean']:.0f} µg/m³", f"{NB03}, section 5.2; figure B2")
add(15, "Mean NO₂, stagnant vs particle smog", f"{prof.loc[1, 'no2_mean']:.0f} vs {prof.loc[2, 'no2_mean']:.0f} µg/m³", f"{NB03}, section 5.2; figure B2")
add(15, "NO₂ winter/summer, stagnant vs particle smog", f"{prof.loc[1, 'no2_winter_summer']:.2f} vs {prof.loc[2, 'no2_winter_summer']:.2f}", f"{NB03}, section 5.2; figure B2")

smog = cities[cities["cluster_k2"] == 1]
add(14, "Winter-smog cluster: Po Valley / Polish / other cities",
    f"{int((smog['group'] == 'Po Valley').sum())} (all of them) / {int((smog['group'] == 'Poland').sum())} / {int((smog['group'] == 'Rest of Europe').sum())}", f"{NB03}, section 5.5")
part = cities[cities["cluster_k4"] == 2]
add(16, "Particle-smog cluster: Polish cities", f"{int((part['group'] == 'Poland').sum())} of {len(part)}", f"{NB03}, section 5.5")

pcs = PCA().fit(X).transform(X)[:, :3]
ms = []
for q in (0.2, 0.25, 0.3):
    labels = MeanShift(bandwidth=estimate_bandwidth(pcs, quantile=q, random_state=0)).fit_predict(pcs)
    ms.append((len(set(labels)), adjusted_rand_score(labels, cities["cluster_k2"])))
add(16, "Mean-shift: clusters found; agreement with k-means k = 2 (ARI)",
    f"{', '.join(str(v) for v in sorted(set(m[0] for m in ms)))} for every bandwidth; {min(m[1] for m in ms):.2f}–{max(m[1] for m in ms):.2f}", f"{NB03}, section 6")
reference = KMeans(n_clusters=2, n_init=50, random_state=0).fit_predict(X)
core = reference == np.argmin(np.bincount(reference))
rng_core, kept = np.random.default_rng(0), 0          # notebook 03, section 4.3
for b in range(100):
    sample = rng_core.integers(0, len(X), len(X))
    labels = KMeans(n_clusters=2, n_init=10, random_state=b).fit(X[sample]).predict(X)
    small = labels == np.argmin(np.bincount(labels))
    kept += int((small & core).sum() == core.sum())
add(16, "Resamples in which all 35 winter-smog cities stay together", f"{kept} of 100", f"{NB03}, section 4.3")
complete = cities["pm25_mean"].notna() & cities["pm25_pm10_ratio"].notna()
sub = cities[complete]
lab = pd.Series(KMeans(n_clusters=2, n_init=50, random_state=0).fit_predict(
    StandardScaler().fit_transform(sub[FEATURES + ["pm25_mean", "pm25_pm10_ratio"]])), index=sub.index)
polluted = lab == sub.groupby(lab)["pm10_mean"].mean().idxmax()
add(16, "With PM2.5 (244 cities): polluted cluster size; core kept; Polish cities in it",
    f"{int(polluted.sum())}; {int((polluted & (sub['cluster_k2'] == 1)).sum())} of {int((sub['cluster_k2'] == 1).sum())}; "
    f"{int((polluted & (sub['group'] == 'Poland')).sum())}", f"{NB03}, section 8")

wind = cities.groupby("cluster_k4")["wind_winter"].median()
add(17, "Median winter wind by cluster (stagnant / particle / moderate / clean)", " / ".join(f"{wind[c]:.1f}" for c in range(1, 5)) + " m/s", f"{NB03}, section 7; figure B4")
def eps2(column, var):
    groups = [cities.loc[cities[column] == c, var] for c in sorted(cities[column].unique())]
    h = stats.kruskal(*groups).statistic
    return max(0, (h - len(groups) + 1) / (len(cities) - len(groups)))
add(17, "Effect size ε² of winter wind, k = 2 / k = 4", f"{eps2('cluster_k2', 'wind_winter'):.2f} / {eps2('cluster_k4', 'wind_winter'):.2f}", f"{NB03}, section 7; figure B4")
add(17, "Effect size ε² of population, k = 2 / k = 4", f"{eps2('cluster_k2', 'log_population'):.2f} / {eps2('cluster_k4', 'log_population'):.2f}", f"{NB03}, section 7")
cold = cities.groupby("cluster_k4")[["temperature_winter", "frost_days_year", "dist_sea_km"]].median()
add(17, "Particle smog: median winter temperature; frost days; distance from sea",
    f"{cold.loc[2, 'temperature_winter']:.1f} °C; {cold.loc[2, 'frost_days_year']:.0f} days; {cold.loc[2, 'dist_sea_km']:.0f} km", f"{NB03}, section 7")

scores = PCA().fit(X).transform(X)
add(18, "Milan's rank on PC1 (general pollution level)", f"{int((scores[:, 0] > scores[milan.name, 0]).sum()) + 1} of {n}", f"{NB03}, section 9; figure B5")
exc = cities.groupby("cluster_k4")["exceeds_pm10_limit"].agg(["sum", "size"])
add(18, "Cities over the exceedance indicator, stagnant / particle / moderate / clean",
    " / ".join(f"{int(exc.loc[c, 'sum'])} of {int(exc.loc[c, 'size'])}" for c in range(1, 5)), f"{NB03}, section 7")


# ---------------------------------------------------------------------------------------------
# Block C (slides 20-26):
# read from the outputs of notebook 04
# ---------------------------------------------------------------------------------------------
PROCESSED = os.path.join(ROOT, "data", "processed")
clf = pd.read_csv(os.path.join(PROCESSED, "classification.csv"))
models = pd.read_csv(os.path.join(PROCESSED, "classification_models.csv"))
checks = pd.read_csv(os.path.join(PROCESSED, "classification_checks.csv"))
clf = clf.merge(cities[["country", "city", "wind_winter", "temperature_winter"]], on=["country", "city"])
y = clf["exceeds_pm10_limit"].astype(int)

def model_row(predictors, model, cv):
    return models[(models["predictors"] == predictors) & (models["model"] == model) & (models["cross-validation"] == cv)].iloc[0]

def auc_text(r, interval=True):
    return f"{r['AUC']:.2f} [{r['AUC 95% low']:.2f}–{r['AUC 95% high']:.2f}]" if interval else f"{r['AUC']:.2f}"

def check(name, item=None):
    rows_ = checks[checks["check"] == name]
    return rows_ if item is None else rows_[rows_["item"] == item].iloc[0]

# Slide 20: target, baseline, why the random split is too easy
add(20, "Cities over the PM10 exceedance indicator", f"{int(y.sum())} of {len(y)} ({y.mean():.1%})", f"{NB04}, section 1")
add(20, "'Always no': accuracy; AUC; average precision of a model with no skill", f"{1 - y.mean():.3f}; 0.5; {y.mean():.3f}", f"{NB04}, section 1")
add(20, "Class weights: one city over the limit counts as many cities under it as", f"{(len(y) - y.sum()) / y.sum():.2f}", f"{NB04}, section 1")
same = check("cities with identical weather", "cities")
# Target sensitivity to missing days: counts scaled by days in the year / valid days (a check, not a correction)
pm = pd.read_csv(os.path.join(ROOT, "data", "interim", "coverage_pm_station_years.csv"))
pm = pm[(pm["pollutant"] == "PM10") & pm["year"].between(2016, 2023) & (pm["valid_days"] >= 274)]
pm = pm.merge(clf[["country", "city"]], on=["country", "city"])
days_in_year = np.where(pm["year"] % 4 == 0, 366, 365)
pm["annualised"] = pm["days_above_50"] * days_in_year / pm["valid_days"]
annualised = pm.groupby(["country", "city", "year"])["annualised"].mean().groupby(["country", "city"]).mean()
crossing = annualised[(annualised > 35)].index.get_level_values("city").difference(clf.loc[y == 1, "city"])
add(20, "Cities over 35 observed days; if missing days are annualised (which cities cross)",
    f"{int(y.sum())}; {int((annualised > 35).sum())} ({', '.join(sorted(crossing))})", f"{NB04}, section 1")
add(21, "Cities sharing all 10 weather values with another city (same NASA POWER cell)", f"{int(same['n'])} ({int(same['k'])} groups; e.g. Milano–Bergamo, Katowice–Zabrze)", f"{NB04}, sections 3 and 7")

# Slide 23: model comparison (figure C1)
f_r, f_g = model_row("M1 weather", "Random forest", "random"), model_row("M1 weather", "Random forest", "geographic")
add(22, "Random forest, weather only: AUC random / geographic [95% interval]", f"{auc_text(f_r, False)} / {auc_text(f_g)}", f"{NB04}, section 5; figure C1")
add(22, "Random forest, weather only: average precision, geographic (no skill = 0.106)", f"{f_g['average precision']:.2f}", f"{NB04}, section 5")
l_r, l_g = model_row("M1 weather", "Logistic regression", "random"), model_row("M1 weather", "Logistic regression", "geographic")
add(22, "Logistic regression, weather: AUC random / geographic [95% interval]", f"{auc_text(l_r, False)} / {auc_text(l_g)}", f"{NB04}, section 5; figure C1")
geo_all = models[models["cross-validation"] == "geographic"]
low = geo_all.loc[geo_all["AUC"].idxmin()]
add(22, f"Lowest geographic AUC of all {len(geo_all)} models", f"{auc_text(low)} ({low['model']}, {low['predictors']})", f"{NB04}, section 5")
m3 = model_row("M3 + population", "Random forest", "geographic")
d = check("AUC difference, weather only minus with population (geographic)", "random forest")
add(22, "Random forest with population: geographic AUC; difference from weather only (paired bootstrap)", f"{auc_text(m3)}; {d['value']:.2f} [{d['low']:.2f}–{d['high']:.2f}]", f"{NB04}, section 5")
add(24, "Cities over the limit flagged (score ≥ 0.5), forest weather only, geographic", f"{int(((clf['score_geographic'] >= 0.5) & (y == 1)).sum())} of {int(y.sum())}", f"{NB04}, section 5")
flag = clf["score_geographic"] >= 0.5
tp, fp = int((flag & (y == 1)).sum()), int((flag & (y == 0)).sum())
add("22, 24", "At score ≥ 0.5: found / missed / false alarms; precision", f"{tp} / {int(y.sum()) - tp} / {fp}; {tp}/{tp + fp} = {tp / (tp + fp):.2f}", f"{NB04}, section 5")
ms = check("mean score vs real share", "weather-only forest, geographic")
add(22, "Scores are not probabilities: mean score vs real share over the limit", f"{ms['value']:.2f} vs {ms['low']:.2f}", f"{NB04}, section 5")

# Slide 24: which weather the forest needs (figure C2)
fam = check("importance, family").set_index("item")
add(23, "Drop in AUC, families shuffled together: wind / temperature family / humidity (median)",
    f"{fam.loc['Wind (year + winter)', 'value']:.2f} / {fam.loc['Temperature family', 'value']:.2f} / {fam.loc['Humidity', 'value']:.3f}", f"{NB04}, section 6; figure C2")
single = check("importance, single").set_index("item")
add(23, "Drop in AUC, one at a time: yearly wind / winter wind (median)", f"{single.loc['Wind (year)', 'value']:.3f} / {single.loc['Winter wind', 'value']:.3f}", f"{NB04}, section 6")
rest = fam.drop(["Wind (year + winter)", "Temperature family", "Humidity"])
add(23, "Not drawn (no loss): " + ", ".join(rest.index) + " (median drop in AUC)",
    " / ".join(f"{v:.3f}" for v in rest["value"]), f"{NB04}, section 6; caption of figure C2")

# Slide 25: which cities are found (figure C3)
over = clf[y == 1]
po, pl = over[over["group"] == "Po Valley"], over[over["group"] == "Poland"]
add(24, "Po Valley cities over the limit flagged; Polish ones flagged (geographic CV)",
    f"{int((po['score_geographic'] >= 0.5).sum())} of {len(po)}; {int((pl['score_geographic'] >= 0.5).sum())} of {len(pl)}", f"{NB04}, section 7; figure C3")
near = po[(po["score_geographic"] >= 0.5) & (po["score_geographic"] < 0.53)].sort_values("score_geographic", ascending=False)
add(24, "Po Valley cities just above the threshold", ", ".join(f"{c} {p:.2f}" for c, p in zip(near["city"], near["score_geographic"])), f"{NB04}, section 7")
pol = clf[clf["group"] == "Poland"].groupby("exceeds_pm10_limit")[["wind_winter", "temperature_winter"]].median()
add(24, "Polish cities over vs under the limit: median winter wind; winter temperature",
    f"{pol.loc[True, 'wind_winter']:.1f} vs {pol.loc[False, 'wind_winter']:.1f} m/s; {pol.loc[True, 'temperature_winter']:.1f} vs {pol.loc[False, 'temperature_winter']:.1f} °C", f"{NB04}, section 7")
add(24, "AUC among the 32 Polish cities only", f"{check('AUC among the Polish cities only (geographic scores)', 'Poland')['value']:.2f}", f"{NB04}, section 7")
fa = clf[(clf["score_geographic"] >= 0.5) & (y == 0)]
add(24, "False alarms; of them Italian", f"{len(fa)}; {int((fa['country'] == 'IT').sum())}", f"{NB04}, section 7")
k = clf[clf["city"] == "Kraków"].iloc[0]
add(24, "Kraków: score random / geographic", f"{k['score_random']:.2f} / {k['score_geographic']:.2f}", f"{NB04}, section 7")

# Slide 25: how strict is the test (figure C4)
auc_split = check("AUC by split").set_index("item")["value"]
for split in ["random", "12 geographic blocks", "one country left out"]:
    add(25, f"AUC, {split}: weather / latitude and longitude only",
        f"{auc_split[f'weather (M1) | {split}']:.2f} / {auc_split[f'latitude and longitude only | {split}']:.2f}", f"{NB04}, section 7; figure C4")
for _, r in check("hold-out, Po Valley over the limit flagged").iterrows():
    add(25, f"Po Valley cities over the limit flagged — {r['item']}", f"{int(r['k'])} of {int(r['n'])}", f"{NB04}, section 7; figure C4")

# Slide 26: the answer (figure C5)
for number, name in [(1, "stagnant winter smog"), (2, "cold-winter particle smog")]:
    part = clf[(clf["cluster_k4"] == number) & (y == 1)]
    add(26, f"Cluster {name}: cities over the limit flagged", f"{int((part['score_geographic'] >= 0.5).sum())} of {len(part)}", f"{NB04}, section 8; figure C5")
m = clf[clf["city"].str.startswith("Milano")].iloc[0]
same_cluster = clf[clf["cluster_k4"] == m["cluster_k4"]].sort_values("score_geographic", ascending=False).reset_index(drop=True)
s_cl, s_m = same_cluster["score_geographic"], m["score_geographic"]   # exact ties (Milano and Bergamo share the same weather)
rank_hi, rank_lo = int((s_cl > s_m).sum()) + 1, int((s_cl >= s_m).sum())
rank_text = f"{rank_hi}–{rank_lo} (tied)" if rank_lo > rank_hi else f"{rank_hi}"
add(26, "Milan: score random / geographic; rank in its cluster; cluster median",
    f"{m['score_random']:.2f} / {m['score_geographic']:.2f}; {rank_text} of {len(same_cluster)}; {same_cluster['score_geographic'].median():.2f}", f"{NB04}, section 8; figure C5")

# ---------------------------------------------------------------------------------------------
# Write the file
# ---------------------------------------------------------------------------------------------
lines = ["# Numbers of the presentation (opening, blocks A, B and C)", "",
         "Written by `src/make_numbers.py` from `data/processed/cities.csv`, `clusters.csv` and the three",
         "`classification*.csv` files of notebook 04: do not edit by hand, run the script again (after notebook 04).",
         "Slide numbers follow the final deck (28 slides): opening and block A 1–10, block B 11–18, block C 19–27.",
         "\"backup\" = not on a slide, ready for questions.",
         "Block C scores are class-weighted model scores, not probabilities.", "",
         "| Slide | What | Value | Source |", "| --- | --- | --- | --- |"]
order = lambda r: (1, 0) if r[0] == "backup" else (0, int(str(r[0]).split(",")[0]))   # by slide, backup last
lines += [f"| {s} | {w} | {v} | {src} |" for s, w, v, src in sorted(rows, key=order)]
with open(os.path.join(ROOT, "slides", "NUMBERS.md"), "w") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))
