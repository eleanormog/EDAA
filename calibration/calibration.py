### calibration.py ###

# this script uses the reference data to calibrate monitor A12
import matplotlib
matplotlib.use("Agg")

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# output directory (relative path: outputs/calibration_plots)
output_dir = Path("outputs/calibration_plots")
output_dir.mkdir(parents=True, exist_ok=True)

# load in the data using relative paths
ref_data = pd.read_csv("calibration\lab_ref_co2_5min_101026_131026.csv") # ref_data date runs from 10/10/2026 to 14/10/2026
sensor_data = pd.read_csv("calibration\export.csv") # for sensor A12

# fix time formatting and set time ot be the index
ref_data["datetime_utc"] = pd.to_datetime(ref_data["datetime_utc"], utc=True)
ref_data.set_index("datetime_utc", inplace=True)

sensor_data["UTC Date/Time"] = pd.to_datetime(
    sensor_data["UTC Date/Time"], utc=True
)
sensor_data.set_index("UTC Date/Time", inplace=True)
sensor_data.sort_index(inplace=True)
sensor_data.index = (
    sensor_data.index - pd.Timedelta(hours=1)
)  # 1 hour time lag correction

# compare reference data to sensor data by merging on time index
combined = pd.concat(
    [ref_data["ref_co2_ppm"], sensor_data["CO2 (ppm) raw"]], axis=1
).dropna()

# define axis boundaries for 1:1 ref line
min_val = min(combined["ref_co2_ppm"].min(), combined["CO2 (ppm) raw"].min())
max_val = max(combined["ref_co2_ppm"].max(), combined["CO2 (ppm) raw"].max())

# 1.  time series plot of both ref & raw sensor on the same time axis
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(
    combined.index,
    combined["ref_co2_ppm"],
    label="Reference CO2",
    color="black",
    linewidth=1.2,
)
ax.plot(
    combined.index,
    combined["CO2 (ppm) raw"],
    label="Raw Sensor (A12)",
    color="tab:blue",
    alpha=0.8,
    linewidth=1.2,
)
ax.set_xlabel("UTC Date/Time")
ax.set_ylabel("CO2 (ppm)")
ax.set_title("Time Series: Reference vs Raw Sensor CO2")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d %H:%M"))
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.savefig(output_dir / "co2_time_series.png", dpi=300)
plt.close()

# 2. raw scatter plot with 1:1 reference line (m=1) 
# & cmap over time (to see old to new values)
fig, ax = plt.subplots(figsize=(9, 6))

# Map datetime index to numeric format for color scale
time_numeric = mdates.date2num(combined.index)

scatter = ax.scatter(
    combined["ref_co2_ppm"],
    combined["CO2 (ppm) raw"],
    c=time_numeric,
    cmap="viridis",
    alpha=0.6,
    edgecolors="none",
)

# Add 1:1 reference line
ax.plot([min_val, max_val], [min_val, max_val], "r--", label="m = 1 Line (1:1)")

# Add and format colorbar for date/time
cbar = fig.colorbar(scatter, ax=ax)
cbar.ax.yaxis.set_major_formatter(mdates.DateFormatter("%b %d %H:%M"))
cbar.set_label("UTC Date/Time")

ax.set_xlabel("Reference CO2 (ppm)")
ax.set_ylabel("Raw Sensor CO2 (ppm)")
ax.set_title("Monitor A12 Raw vs Reference CO2 (Time Evolution)")
ax.legend(loc="upper left")
ax.grid(True)
plt.tight_layout()
plt.savefig(output_dir / "raw_vs_ref_scatter.png", dpi=300)
plt.close()


# 3. linear fit (np.polyfit) & cov matrix calc
p, cov = np.polyfit(
    combined["ref_co2_ppm"], combined["CO2 (ppm) raw"], 1, cov=True
)
slope, intercept = p[0], p[1]

print(f"fit equation: raw CO2 = {slope:.10f} * ref + ({intercept:.10f})")
print("covariance matrix for uncertainty propagation:")
print(cov)

# 4. calculate calibrated CO2 values: Calibrated = (Raw - Intercept) / Slope
combined["CO2 (ppm) calibrated"] = (
    combined["CO2 (ppm) raw"] - intercept
) / slope

# 5. calibrated scatter plot vs 1:1 line
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(
    combined["ref_co2_ppm"],
    combined["CO2 (ppm) calibrated"],
    alpha=0.3,
    color="green",
    label="Calibrated Sensor",
)
ax.plot([min_val, max_val], [min_val, max_val], "r--", label="m = 1 Line (1:1)")
ax.set_xlabel("Reference CO2 (ppm)")
ax.set_ylabel("Calibrated Sensor CO2 (ppm)")
ax.set_title("Monitor A12 Calibrated vs Reference CO2")
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.savefig(output_dir / "calibrated_vs_ref_scatter.png", dpi=300)
plt.close()

# 6. time series plot with ref data and calibrated CO2 sensor data
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(
    combined.index,
    combined["ref_co2_ppm"],
    label="Reference CO2",
    color="black",
    linewidth=1.2,
)
ax.plot(
    combined.index,
    combined["CO2 (ppm) calibrated"],
    label="Calibrated Sensor (A12)",
    color="tab:green",
    alpha=0.8,
    linewidth=1.2,
)
ax.set_xlabel("Time")
ax.set_ylabel("CO2 (ppm)")
ax.set_title("Time Series: Reference vs Calibrated Sensor CO2")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d %H:%M"))
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.savefig(output_dir / "co2_time_series_calibrated.png", dpi=300)
plt.close()

# save the combined dataset for future reference
combined.to_csv(output_dir / "calibrated_A12_data.csv")
