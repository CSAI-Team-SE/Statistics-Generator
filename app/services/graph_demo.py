# imports
import csv
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import io
import re
import os
from scipy.stats import ttest_ind

# ---------------------------------------------------------
# load CSV in
# ---------------------------------------------------------
with open("earthquake_data_tsunami.csv", "r") as csv_file:
    rows = list(csv.DictReader(csv_file))

# ---------------------------------------------------------
# columns in CSV and the user input (menu choise)
# ---------------------------------------------------------
COLUMN_MAP = {
    "a": "magnitude",
    "b": "cdi",
    "c": "mmi",
    "d": "sig",
    "e": "nst",
    "f": "dmin",
    "g": "gap",
    "h": "depth",
    "i": "latitude",
    "j": "longitude",
    "k": "Year",
    "l": "Month",
    "m": "tsunami"
}

# ---------------------------------------------------------
# cleaning and getting column
# ---------------------------------------------------------
# covert into a float where possible
def convert(value):
    try:
        return float(value)
    except:
        return None

# get column names from user input and create list of data
def get_column(indicator):
    label = COLUMN_MAP[indicator]
    data = [convert(row[label]) for row in rows]
    data = [x for x in data if x is not None]
    return label, data

# ---------------------------------------------------------
# hnadle inputs (irrelivent when adding to website)
# ---------------------------------------------------------
def get_choice(prompt, options):
    attempts = 0
    choice = ""
    while choice not in options:
        if attempts > 0:
            print("\nERROR — PLEASE TRY AGAIN\n")
        attempts += 1
        choice = input(prompt).lower()
    return choice

# ---------------------------------------------------------
# GRAPH LIBRARY — normal graph for user defined axis
# ---------------------------------------------------------
def graph_scatter(x_label, x_axis, y_label, y_axis, title):
    plt.scatter(x_axis, y_axis, alpha=0.6)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)

def graph_line(x_label, x_axis, y_label, y_axis, title):
    plt.plot(x_axis, y_axis, linewidth=2)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)

def graph_bar(x_label, x_axis, y_label, y_axis, title):
    plt.bar(x_axis, y_axis)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)

def graph_histogram(x_label, x_axis, y_label, y_axis, title):
    plt.hist(x_axis, bins=30, alpha=0.7, label=x_label)
    plt.hist(y_axis, bins=30, alpha=0.7, label=y_label)
    plt.legend()
    plt.title(title)

def graph_boxplot(x_label, x_axis, y_label, y_axis, title):
    plt.boxplot([x_axis, y_axis], labels=[x_label, y_label])
    plt.title(title)

def graph_heatmap(x_label, x_axis, y_label, y_axis, title):
    plt.hist2d(x_axis, y_axis, bins=40, cmap="plasma")
    plt.colorbar(label="Density")
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)

# ---------------------------------------------------------
# GRAPH LIBRARY — special graphs (no user axis)
# ---------------------------------------------------------
def graph_quakes_per_year():
    _, years = get_column("k") # lable not needed
    years = [int(y) for y in years] # turn years into ints
    counts = Counter(years) # count how many times each year appears
    xs = sorted(counts.keys()) # put years in order
    ys = [counts[y] for y in xs]
    plt.bar(xs, ys)
    plt.xlabel("Year")
    plt.ylabel("Earthquake Count")
    plt.title("Earthquakes Per Year")
    return xs, ys

def graph_quakes_per_month():
    _, months = get_column("l") # lable not needed
    months = [int(m) for m in months] # turn months into ints
    counts = Counter(months) # how many times each months appears
    xs = sorted(counts.keys()) # put in order
    ys = [counts[m] for m in xs]
    plt.bar(xs, ys)
    plt.xlabel("Month")
    plt.ylabel("Earthquake Count")
    plt.title("Earthquakes Per Month")
    return xs, ys

def graph_avg_magnitude_per_year():
    _, years = get_column("k") # lable not needed
    _, mags = get_column("a") # lable not needed
    years = [int(y) for y in years] # years into ints
    # make a dictionary for magnitude in each year
    data = {}
    for y, m in zip(years, mags):
        data.setdefault(y, []).append(m)
    xs = sorted(data.keys()) # years in order
    ys = [sum(data[y]) / len(data[y]) for y in xs] # get magnitude avrage
    plt.plot(xs, ys, marker="o")
    plt.xlabel("Year")
    plt.ylabel("Average Magnitude")
    plt.title("Average Magnitude Per Year")
    return xs, ys

def graph_tsunamis_per_year():
    _, years = get_column("k")
    _, tsu = get_column("m")
    years = [int(y) for y in years]
    tsu = [int(t) for t in tsu]
    counts = Counter(y for y, t in zip(years, tsu) if t == 1)
    xs = sorted(counts.keys())
    ys = [counts[y] for y in xs]
    plt.bar(xs, ys)
    plt.xlabel("Year")
    plt.ylabel("Tsunami Events")
    plt.title("Tsunamis Per Year")
    return xs, ys

def graph_depth_distribution():
    _, depth = get_column("h")
    plt.hist(depth, bins=40)
    plt.xlabel("Depth (km)")
    plt.ylabel("Frequency")
    plt.title("Depth Distribution")
    return depth 

def graph_location_map():
    _, lat = get_column("i")
    _, lon = get_column("j")
    plt.scatter(lon, lat, alpha=0.5)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Earthquake Locations")
    return lat, lon


# ---------------------------------------------------------
# save graph as bytes (for html)
# ---------------------------------------------------------
def get_graph_bytes():
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    buf.seek(0)
    return buf.getvalue()

def title_to_filename(title):
    # Remove characters not allowed in filenames
    safe = re.sub(r'[^a-zA-Z0-9_\- ]', '', title)
    # Replace spaces with underscores
    safe = safe.replace(" ", "_")
    return safe + ".png"

# ---------------------------------------------------------
# menu outputs
# ---------------------------------------------------------
AXIS_MENU = (
    " a) magnitude\n b) cdi\n c) mmi\n d) sig\n e) nst\n f) dmin\n"
    " g) gap\n h) depth\n i) latitude\n j) longitude\n k) Year\n"
    " l) Month\n m) tsunami\n\nSELECT LETTER: "
)

GRAPH_MENU = (
    " a) Scatter Plot\n"
    " b) Line Plot\n"
    " c) Bar Chart\n"
    " d) Histogram\n"
    " e) Box Plot\n"
    " f) Heatmap (X vs Y density)\n"
    " g) Earthquakes Per Year\n"
    " h) Earthquakes Per Month\n"
    " i) Average Magnitude Per Year\n"
    " j) Tsunami Events Per Year\n"
    " k) Depth Distribution\n"
    " l) Location Map (Latitude vs Longitude)\n\nSELECT LETTER: "
)

SPECIAL_GRAPHS = ["g", "h", "i", "j", "k", "l"]

# ---------------------------------------------------------
# graph type selection
# ---------------------------------------------------------
graph_type = get_choice("Select graph type:\n" + GRAPH_MENU,
                        ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"])

title = input("Graph Title: ")
# ---------------------------------------------------------
# title, x and y user inputs (asked for only for standard graphs)
# ---------------------------------------------------------

if graph_type not in SPECIAL_GRAPHS:
    x_indicator = get_choice("Select X axis:\n" + AXIS_MENU, COLUMN_MAP.keys())
    y_indicator = get_choice("Select Y axis:\n" + AXIS_MENU, COLUMN_MAP.keys())

    x_label, x_axis = get_column(x_indicator)
    y_label, y_axis = get_column(y_indicator)

    min_len = min(len(x_axis), len(y_axis))
    x_axis = x_axis[:min_len]
    y_axis = y_axis[:min_len]

# ---------------------------------------------------------
# plotting for all graphs
# ---------------------------------------------------------
plt.style.use("seaborn-v0_8-darkgrid")
plt.figure(figsize=(10, 6))

if graph_type == "a":
    graph_scatter(x_label, x_axis, y_label, y_axis, title)
elif graph_type == "b":
    graph_line(x_label, x_axis, y_label, y_axis, title)
elif graph_type == "c":
    graph_bar(x_label, x_axis, y_label, y_axis, title)
elif graph_type == "d":
    graph_histogram(x_label, x_axis, y_label, y_axis, title)
elif graph_type == "e":
    graph_boxplot(x_label, x_axis, y_label, y_axis, title)
elif graph_type == "f":
    graph_heatmap(x_label, x_axis, y_label, y_axis, title)
elif graph_type == "g":
    x_axis, y_label= graph_quakes_per_year()
elif graph_type == "h":
    x_axis, y_label= graph_quakes_per_month()
elif graph_type == "i":
    x_axis, y_label = graph_avg_magnitude_per_year()
elif graph_type == "j":
    x_axis, y_label = graph_tsunamis_per_year()
elif graph_type == "k":
    x_axis, y_label = graph_depth_distribution()
elif graph_type == "l":
    x_axis, y_label = graph_location_map()


# ---------------------------------------------------------
# basic show graph
# ---------------------------------------------------------
# plt.tight_layout()
# plt.show()

# ---------------------------------------------------------
# get graph bytes and save png
# ---------------------------------------------------------
plt.tight_layout()

# get PNG bytes
img_bytes = get_graph_bytes()

# ensure graphs folder exists
output_dir = "graphs"
os.makedirs(output_dir, exist_ok=True)

# save to a file (can be removed when html is complete)
filename = title_to_filename(title)
filepath = os.path.join(output_dir, filename)
with open(filepath, "wb") as f:
    f.write(img_bytes)

print(f"Graph saved as {filepath}")
print("Range: ",  max(y_axis) - min(y_axis))
print("P Value: ", ttest_ind(x_axis, y_axis).pvalue)
print("Gradient: ")
print("IQR: ")