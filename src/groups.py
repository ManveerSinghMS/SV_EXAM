"""The shared definitions of the project, used by every notebook: city groups and logarithms.

Usage:
    import sys; sys.path.append("../src")
    from groups import add_groups, add_logs

    cities = add_groups(cities)     # adds the columns "region", "po_valley" and "group"
    cities = add_logs(cities)       # adds the columns "log_population", "log_rain_mm_day", ...

Every rule below is recorded, with its reason, in the README decision log.
"""
import os
import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_REGIONS = os.path.join(_HERE, "..", "data", "external", "italian_cities_regions.csv")

# ---------------------------------------------------------------------------------------------
# 1. The Po Valley, defined by a written rule (geography only, never by pollution values)
# ---------------------------------------------------------------------------------------------
# A city is in the Po Valley if:
#   - it is in one of the four regions of the plain between the Alps and the Apennines,
#   - it is below 300 m of altitude,
#   - it is not in an Alpine or pre-Alpine valley (in our data: Lecco, on Lake Como).
# Result: 25 cities. Rimini is in (Romagna plain, like Ravenna); Udine, Trento, Trieste, Genova are out
# (other regions, or not in the plain).
PO_VALLEY_REGIONS = ["Piemonte", "Lombardia", "Emilia-Romagna", "Veneto"]
PO_VALLEY_MAX_ALTITUDE = 300

# ---------------------------------------------------------------------------------------------
# 2. The three groups used in every figure (descriptive only: they never enter clustering or models)
# ---------------------------------------------------------------------------------------------
# Group names: "Po Valley", "Poland", "Rest of Europe" (order and colours in src/style.py).


def add_groups(cities):
    """Add 'region' (Italian cities only), 'po_valley' (True/False) and 'group' (Po Valley / Poland / Rest of Europe)."""
    cities = cities.copy()
    regions = pd.read_csv(_REGIONS)
    region = cities["city"].map(regions.set_index("city")["region"])
    valley = cities["city"].map(regions.set_index("city")["alpine_or_prealpine_valley"]).fillna(False).astype(bool)
    cities["region"] = region.where(cities["country"] == "IT")
    cities["po_valley"] = (
        (cities["country"] == "IT")
        & region.isin(PO_VALLEY_REGIONS)
        & (cities["altitude"] < PO_VALLEY_MAX_ALTITUDE)
        & ~valley
    )
    cities["group"] = np.select([cities["po_valley"], cities["country"].eq("PL")],
                                ["Po Valley", "Poland"], "Rest of Europe")
    return cities


# ---------------------------------------------------------------------------------------------
# 3. Logarithms of the strongly skewed variables
# ---------------------------------------------------------------------------------------------
# Why: k-means, PCA (block B) and logistic regression (block C) work with distances or straight lines,
# so a variable with a long right tail lets a few extreme cities dominate. The logarithm compresses the
# tail. (A random forest and Spearman correlation do not need it: they only use the order of the values.)
# Skewness before -> after (notebook 02, section 3.4):
#   population 7.2 -> 1.2, rain 2.5 -> 0.3, days PM10 > 50 1.8 -> 0.1, PM10 winter/summer 1.2 -> 0.4.
# PM10 winter/summer is a ratio: on a log scale "twice" and "half" are symmetric around 0.
LOG_VARIABLES = ["population", "rain_mm_day", "pm10_days_above_50", "pm10_winter_summer"]
# Altitude contains 0 m, and log(0) does not exist: we use log(1 + x). Skewness 1.8 -> -0.7.
LOG1P_VARIABLES = ["altitude"]
# Not transformed: the winter mixing layer (skewness 1.8 -> only 1.3 with the log, and it is a weak,
# rough variable anyway), and all the other variables (skewness below 1).


def add_logs(cities):
    """Add a column 'log_<name>' for each variable in LOG_VARIABLES and LOG1P_VARIABLES (originals are kept)."""
    cities = cities.copy()
    for var in LOG_VARIABLES:
        cities["log_" + var] = np.log(cities[var])
    for var in LOG1P_VARIABLES:
        cities["log_" + var] = np.log1p(cities[var])
    return cities
