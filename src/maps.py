"""Maps of Europe without extra libraries (no geopandas or cartopy needed).

Usage in a notebook:

    import sys; sys.path.append("../src")
    from maps import draw_europe, to_map

    fig, ax = plt.subplots(figsize=(8, 8))
    draw_europe(ax)                                   # land, sea, borders, extent
    x, y = to_map(cities["lon"], cities["lat"])       # longitude/latitude -> map coordinates
    ax.scatter(x, y, ...)

Projection: Lambert azimuthal equal-area centred on Europe (EPSG:3035, "ETRS89-LAEA").
It is the projection the European Environment Agency uses for its own maps, and it is
equal-area: a country keeps its true size relative to the others, which a plain
longitude/latitude plot does not do (northern Europe looks too wide there).
Basemap: Natural Earth 1:50m countries (public domain), in data/external/countries_europe.geojson.
"""
import json
import os
import numpy as np
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

from style import LAND, SEA, BORDER

_HERE = os.path.dirname(os.path.abspath(__file__))
_COUNTRIES = os.path.join(_HERE, "..", "data", "external", "countries_europe.geojson")

# EPSG:3035 parameters: centre 52°N 10°E, false easting/northing in metres; Earth as a sphere
# (the difference from the exact ellipsoid formula is a few km, invisible at this scale).
_LAT0, _LON0, _X0, _Y0, _R = np.radians(52), np.radians(10), 4321000, 3210000, 6371007


def to_map(lon, lat):
    """Convert longitude and latitude (degrees) into map coordinates (metres, EPSG:3035)."""
    lon, lat = np.radians(np.asarray(lon, dtype=float)), np.radians(np.asarray(lat, dtype=float))
    k = np.sqrt(2 / (1 + np.sin(_LAT0) * np.sin(lat) + np.cos(_LAT0) * np.cos(lat) * np.cos(lon - _LON0)))
    x = _R * k * np.cos(lat) * np.sin(lon - _LON0) + _X0
    y = _R * k * (np.cos(_LAT0) * np.sin(lat) - np.sin(_LAT0) * np.cos(lat) * np.cos(lon - _LON0)) + _Y0
    return x, y


# Default extent: from Portugal to Finland and Romania (map coordinates, metres)
EXTENT = (2_550_000, 6_050_000, 1_350_000, 5_350_000)


def draw_europe(ax, extent=EXTENT):
    """Draw the base map: sea as background, land in light grey, thin white borders."""
    countries = json.load(open(_COUNTRIES, encoding="utf-8"))["features"]
    patches = []
    for country in countries:
        for polygon in country["geometry"]["coordinates"]:
            outer = np.array(polygon[0])            # outer ring of the polygon (holes are ignored)
            x, y = to_map(outer[:, 0], outer[:, 1])
            patches.append(Polygon(np.column_stack([x, y]), closed=True))
    ax.add_collection(PatchCollection(patches, facecolor=LAND, edgecolor=BORDER, linewidth=0.5, zorder=0))
    ax.set_facecolor(SEA)
    ax.set_xlim(extent[0], extent[1])
    ax.set_ylim(extent[2], extent[3])
    ax.set_aspect("equal")                          # metres on both axes: no stretching
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    for side in ax.spines.values():
        side.set_visible(False)
