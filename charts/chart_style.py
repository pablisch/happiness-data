# chart_style.py

# -----------------------------
# Typography control
# -----------------------------
FONT_SCALE = 1.5

AXIS_LABEL_SIZE = 13 * FONT_SCALE
TICK_SIZE = 12 * FONT_SCALE

X_LABEL_PADDING = 12 * FONT_SCALE
# -----------------------------

# -----------------------------
# Figure defaults
# -----------------------------
BASE_WIDTH = 12
BASE_HEIGHT_BAR = 8
BASE_HEIGHT_GRAPH = 6
# -----------------------------

# -----------------------------
# Time line graph consts
# -----------------------------
FIXED_GRAPH_MIN = 5
FIXED_GRAPH_MAX = 8
EU_TOTAL_MIN = 6.5
EU_TOTAL_MAX = 6.7
# -----------------------------

# -----------------------------
# Contribution bar chart scale (zoomed)
# - used when fixed_scale is False
# - covers EU averages + one selected country (your existing behaviour)
# -----------------------------
EU_BAR_XMIN = 0.0
EU_BAR_XMAX = 1.85   # rounded slightly for nicer ticks
EU_BAR_XPAD_RATIO = 0.06
# -----------------------------

# -----------------------------
# Contribution bar chart scale (fixed, global)
# - used when fixed_scale is True
# - covers ALL countries across ALL supported years
# -----------------------------
FIXED_BAR_XMIN = -0.65   # from BAR_GLOBAL_MIN_RAW ≈ -1.888 (rounded outward)
FIXED_BAR_XMAX = 2.25    # from BAR_GLOBAL_MAX_RAW = 2.209 (rounded outward)
FIXED_BAR_XPAD_RATIO = 0.06
# -----------------------------

# -----------------------------
# Series colours
# -----------------------------
COUNTRY_COLOR = "#1f77b4"  # default matplotlib blue
EU_COLOR = "#ff7f0e"       # EU reference (bars + line)
# -----------------------------

# -----------------------------
# Score card delta colour scale (country - EU average)
# -----------------------------
EU_DELTA_MIN = -0.32  # paste from script (rounded)
EU_DELTA_MAX =  0.26  # paste from script (rounded)
# -----------------------------

