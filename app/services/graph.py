import pandas as pd
import io
import os
import base64
import matplotlib.pyplot as plt
from collections import Counter
from scipy.stats import ttest_ind
import numpy as np

# import clean dataset
from app.services.dataset import load_cleaned

# special graph options
SPECIAL_GRAPHS = {
    "quakes_per_year",
    "quakes_per_month",
    "avg_mag_per_year",
    "tsunamis_per_year",
    "depth_distribution",
    "location_map"
}

# filter checking
def check_filter(low, high):
    if not low or not high:
        return None
    return float(low), float(high)

# find statistics
def compute_stats(dataset, x_data, y_data):
    x_vals = dataset[x_data].dropna().to_numpy()
    y_vals = dataset[y_data].dropna().to_numpy()

    min_len = min(len(x_vals), len(y_vals))
    x_vals = x_vals[:min_len]
    y_vals = y_vals[:min_len]

    return {
        "mean_x": float(np.mean(x_vals)),
        "mean_y": float(np.mean(y_vals)),
        "range_x": float(np.max(x_vals) - np.min(x_vals)),
        "range_y": float(np.max(y_vals) - np.min(y_vals)),
        "p_value": float(ttest_ind(x_vals, y_vals).pvalue),
        "iqr_x": float(np.percentile(x_vals, 75) - np.percentile(x_vals, 25)),
        "iqr_y": float(np.percentile(y_vals, 75) - np.percentile(y_vals, 25)),
    }

# plots graph, saves image as PNG to images file, and returns a base64 png image
def generate_image(
        dataset: pd.DataFrame,
        title: str,
        x_label: str,
        x_data: str,
        y_label: str,
        y_data: str,
        graph_type: str,
        lat_range=None,
        long_range=None
    ):
    
    # Latitude and Longitude filtering
    if lat_range:
        low, high = lat_range
        dataset = dataset[(dataset["latitude"] >= low) & (dataset["latitude"] <= high)]
    if long_range:
        low, high = long_range
        dataset = dataset[(dataset["longitude"] >= low) & (dataset["longitude"] <= high)]
    
    # get column data
    if graph_type not in SPECIAL_GRAPHS:
        # x_data and y_data are dataset column names
        x_axis = dataset[x_data].dropna().tolist()
        y_axis = dataset[y_data].dropna().tolist()

        # match lengths
        min_len = min(len(x_axis), len(y_axis))
        x_axis = x_axis[:min_len]
        y_axis = y_axis[:min_len]
    else:
        x_axis = y_axis = None

    # plotting
    plt.style.use("seaborn-v0_8-darkgrid")
    plt.figure(figsize=(10, 6))

    if graph_type == "scatter":
        plt.scatter(x_axis, y_axis, alpha=0.6)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)

    elif graph_type == "line":
        plt.plot(x_axis, y_axis, linewidth=2)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)

    elif graph_type == "bar":
        plt.bar(x_axis, y_axis)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)

    elif graph_type == "histogram":
        plt.hist(x_axis, bins=30, alpha=0.7, label=x_label)
        plt.hist(y_axis, bins=30, alpha=0.7, label=y_label)
        plt.legend()
        plt.title(title)

    elif graph_type == "boxplot":
        plt.boxplot([x_axis, y_axis], labels=[x_label, y_label])
        plt.title(title)

    elif graph_type == "heatmap":
        plt.hist2d(x_axis, y_axis, bins=40, cmap="plasma")
        plt.colorbar(label="Density")
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)

    #  special graphs (do not need user axis)
    elif graph_type == "quakes_per_year":
        years = dataset["Year"].dropna().astype(int)
        counts = Counter(years)
        xs = sorted(counts.keys())
        ys = [counts[y] for y in xs]
        plt.bar(xs, ys)
        plt.xlabel("Year")
        plt.ylabel("Earthquake Count")
        plt.title("Earthquakes Per Year")

    elif graph_type == "quakes_per_month":
        months = dataset["Month"].dropna().astype(int)
        counts = Counter(months)
        xs = sorted(counts.keys())
        ys = [counts[m] for m in xs]
        plt.bar(xs, ys)
        plt.xlabel("Month")
        plt.ylabel("Earthquake Count")
        plt.title("Earthquakes Per Month")

    elif graph_type == "avg_mag_per_year":
        years = dataset["Year"].dropna().astype(int)
        mags = dataset["magnitude"].dropna()
        grouped = {}
        for y, m in zip(years, mags):
            grouped.setdefault(y, []).append(m)
        xs = sorted(grouped.keys())
        ys = [sum(grouped[y]) / len(grouped[y]) for y in xs]
        plt.plot(xs, ys, marker="o")
        plt.xlabel("Year")
        plt.ylabel("Average Magnitude")
        plt.title("Average Magnitude Per Year")

    elif graph_type == "tsunamis_per_year":
        years = dataset["Year"].dropna().astype(int)
        tsu = dataset["tsunami"].dropna().astype(int)
        counts = Counter(y for y, t in zip(years, tsu) if t == 1)
        xs = sorted(counts.keys())
        ys = [counts[y] for y in xs]
        plt.bar(xs, ys)
        plt.xlabel("Year")
        plt.ylabel("Tsunami Events")
        plt.title("Tsunamis Per Year")

    elif graph_type == "depth_distribution":
        depth = dataset["depth"].dropna()
        plt.hist(depth, bins=40)
        plt.xlabel("Depth (km)")
        plt.ylabel("Frequency")
        plt.title("Depth Distribution")

    elif graph_type == "location_map":
        lat = dataset["latitude"].dropna()
        lon = dataset["longitude"].dropna()
        plt.scatter(lon, lat, alpha=0.5)
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.title("Earthquake Locations")


    # Convert plot to PNG, save in local
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    plt.close()
    buf.seek(0)

    # Save PNG to images folder with a safe title
    images_dir = "images"
    os.makedirs(images_dir, exist_ok=True)
    safe_title = (title or "graph").replace(" ", "_") 
    file_path = os.path.join(images_dir, f"{safe_title}.png")

    with open(file_path, "wb") as f:
        f.write(buf.getvalue())

    # return base64 to frontend
    return base64.b64encode(buf.read()).decode("utf-8")

# call subprocedures 
def process_graph_request(data: dict):
     # get cleaned dataset
    dataset = load_cleaned()

    # check filters
    lat_range = check_filter(data.get("lat_low"), data.get("lat_high"))
    long_range = check_filter(data.get("long_low"), data.get("long_high"))

    # generate the image
    img_b64 = generate_image(
        dataset=dataset,
        title=data.get("title"),
        x_label=data.get("x_label"),
        x_data=data.get("x_data"),
        y_label=data.get("y_label"),
        y_data=data.get("y_data"),
        graph_type=data.get("graph_type"),
        lat_range=lat_range,
        long_range=long_range
    )

    #  get stats
    stats = {}
    if data.get("graph_type") not in SPECIAL_GRAPHS:
        stats = compute_stats(dataset, data.get("x_data"), data.get("y_data"))

    # return image and stats for output
    return {
        "image": img_b64,
        "stats": stats
    }

# JavaScript image get
# document.getElementById("graph-img").src = "data:image/png;base64," + response.image;

# html image get
# <img id="graph-img">