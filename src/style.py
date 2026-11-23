"""Shared style for all the figures of the project.

Usage, at the start of each notebook:

    import sys; sys.path.append("../src")
    from style import apply_style, CLUSTER_COLOURS, BLUE, GREY, source

    apply_style()

Why one shared file: the same cluster or group must have the same colour in every figure, and
palettes must stay readable by colour-blind people. Change a colour here and it
changes in every figure.
"""
import matplotlib.pyplot as plt

# Text and axis colours
INK = "#0b0b0b"          # titles
INK_2 = "#52514e"        # labels, axes
MUTED = "#8a8984"        # notes, sources
GRID = "#e6e5e1"
BACKGROUND = "#fcfcfb"

# Colour to highlight Milan / the Po Valley cities, and grey for "all the others"
BLUE = "#2a78d6"
GREY = "#c9c8c3"

# Cluster colours (block B): blue, red, yellow, green, bright and clearly different hues.
# Clusters are numbered by mean PM10, from the most polluted (1) down, so the order never depends on k-means' random labels.
# One list per solution, because cluster "2" of k = 2 and cluster "2" of k = 4 are different groups of cities:
#   k = 2: cluster 1 (winter smog, contains all 25 Po Valley cities) = BLUE, the same blue as the Po Valley group and Milan;
#          cluster 2 (the rest of Europe) = GREY, the same grey as the "Rest of Europe" group.
#   k = 4: 1 stagnant smog (Po Valley) = BLUE, 2 particle smog (mostly Poland) = RED, 3 moderate = YELLOW, 4 clean = GREEN.
# This follows the rule of the groups below: a cluster that matches a group takes its colour. Red is not the orange of
# Poland, but stays in the same warm family. Every pair of the four colours is checked to stay distinguishable for
# colour-blind readers (deuteranopia, protanopia, tritanopia; worst pair still well separated), not only neighbours,
# because on a map all clusters touch: the green is a blue-green and the red a cool red, so red and green do not merge.
# Yellow is light: on maps every dot has a grey outline (DOT_EDGE), and text is never written in yellow.
RED = "#d7263d"
YELLOW = "#ffd000"
GREEN = "#00c08b"
CLUSTER_COLOURS = {2: [BLUE, GREY], 4: [BLUE, RED, YELLOW, GREEN]}

# Scale for continuous values (e.g. PM10 map): a single hue, from light to dark
CONTINUOUS_SCALE = "Blues"
# Scale for signed values (above/below an average, e.g. the cluster profiles of figure B2): purple-orange, the same
# scale as the correlations. Not red-blue: red and blue are cluster colours, and a red cell next to the red cluster
# would read as "this is cluster 2". Purple = below, white = at the average, orange = above.
DIVERGING_SCALE = "PuOr_r"

# Scale for correlations (from -1 to +1). Purple-orange (ColorBrewer PuOr): diverging, colour-blind safe,
# and neither end reads as "good" or "bad" (red would suggest danger, but a correlation has no good sign).
CORRELATION_SCALE = "PuOr_r"     # purple = negative, white = 0, orange = positive

# --- Maps (used by src/maps.py) ---
LAND = "#e9e8e4"     # land: light warm grey, so coloured dots stand out
SEA = "#ffffff"      # sea: white, the background
BORDER = "#ffffff"   # country borders: thin white lines, visible but quiet

# --- PM10 classes for maps ---
# Classed scale (5 classes) instead of a continuous one: a reader can match a dot to a class,
# not to a precise shade. Breaks are reference values, not arbitrary:
#   15 = WHO 2021 guideline (annual mean), 20 = new EU annual limit from 2030 (Directive 2024/2881),
#   25 and 30 = steps of 5 above it. (The current EU annual limit, 40, is never reached in our data.)
PM10_BREAKS = [15, 20, 25, 30]
PM10_LABELS = ["< 15", "15–20", "20–25", "25–30", "≥ 30"]
# ColorBrewer "YlOrRd", 5 classes (colorbrewer2.org, colour-blind safe, print friendly), light = clean, dark = polluted
PM10_COLOURS = ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"]

# --- NO2 classes for maps (same logic) ---
#   10 = WHO 2021 guideline (annual mean), 20 = new EU annual limit from 2030, 30 = one step above.
#   (The current EU annual limit, 40, is never reached in our data.)
NO2_BREAKS = [10, 20, 30]
NO2_LABELS = ["< 10", "10–20", "20–30", "≥ 30"]
# ColorBrewer "YlOrRd", 4 classes
NO2_COLOURS = ["#ffffb2", "#fecc5c", "#fd8d3c", "#e31a1c"]

# Grey outline for dots on maps, so that the lightest class stays visible on the light land
DOT_EDGE = "#6b6a66"


def apply_style():
    """Set fonts, colours and grid for all the following figures."""
    plt.rcParams.update({
        "figure.facecolor": BACKGROUND, "axes.facecolor": BACKGROUND, "savefig.facecolor": BACKGROUND,
        "figure.dpi": 110, "savefig.dpi": 200,
        "font.family": "DejaVu Sans", "font.size": 10,
        "axes.edgecolor": "#b5b4ae", "axes.labelcolor": INK_2, "axes.titlecolor": INK,
        "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
        "xtick.color": INK_2, "ytick.color": INK_2,
        "legend.frameon": False,
    })


def show(table, decimals=2):
    """Display a table aligned to the left, with a fixed number of decimals.

    Jupyter and VS Code may centre tables or push them to the right; this keeps every
    table of the project in the same place. Usage: show(cities.head()) instead of cities.head().
    """
    if hasattr(table, "to_frame"):          # a Series (one column) becomes a one-column table
        table = table.to_frame()
    return (table.style
            .format(precision=decimals)
            .set_table_styles([
                {"selector": "", "props": [("margin-left", "0"), ("margin-right", "auto")]},
                {"selector": "th, td", "props": [("text-align", "left"), ("padding", "2px 10px")]},
            ]))


def source(fig, text="Source: EEA (validated E1a data) and EEA In-Situ Station Data on Zenodo, CC BY 4.0; weather NASA POWER."):
    """Write the data source at the bottom left of the figure (it must be cited in every figure)."""
    fig.text(0.01, 0.005, text, fontsize=7.5, color=MUTED, ha="left", va="bottom")


# --- Groups of cities shared by all blocks (see README decision log) ---------------------------
# The RULE that decides which city is in which group is in src/groups.py (add_groups);
# here only the order and the colours, used by every figure.
GROUP_ORDER = ["Po Valley", "Poland", "Rest of Europe"]
# Blue = Po Valley (the same blue as Milan), orange = Poland, grey = context.
# Blue and orange are the safest pair for colour-blind readers. If a cluster in block B matches one of
# these groups, give it the same colour; never use blue or orange for something else in the presentation.
ORANGE = "#eb6834"
GROUP_COLOURS = {"Po Valley": BLUE, "Poland": ORANGE, "Rest of Europe": GREY}
