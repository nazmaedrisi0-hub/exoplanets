import streamlit as st
import pandas as pd
import numpy as np

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Exoplanet Analytics Dashboard",
    layout="wide",
)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("exoplanets.csv")

    # -------- rename for usability --------
    df = df.rename(columns={
        "pl_name": "planet",
        "hostname": "star",
        "discoverymethod": "method",
        "disc_year": "year",
        "pl_orbper": "orbital_period",
        "pl_orbsmax": "semi_major_axis",
        "pl_rade": "radius_earth",
        "pl_bmasse": "mass_earth",
        "pl_orbeccen": "eccentricity",
        "pl_insol": "insolation",
        "pl_eqt": "eq_temp",
        "st_teff": "star_temp",
        "st_rad": "star_radius",
        "st_mass": "star_mass",
        "st_met": "metallicity",
        "sy_dist": "distance_pc",
    })

    # -------- numeric safety --------
    num_cols = [
        "orbital_period", "semi_major_axis", "radius_earth", "mass_earth",
        "eccentricity", "insolation", "eq_temp", "star_temp",
        "star_radius", "star_mass", "metallicity", "distance_pc"
    ]

    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # -------- useful categories --------
    def size_bucket(r):
        if pd.isna(r):
            return "Unknown"
        if r < 1.25:
            return "Earth-size"
        elif r < 2:
            return "Super-Earth"
        elif r < 6:
            return "Neptune-like"
        else:
            return "Gas Giant"

    df["size_type"] = df["radius_earth"].apply(size_bucket)

    def temp_bucket(t):
        if pd.isna(t):
            return "Unknown"
        if t < 200:
            return "Cold"
        elif t < 800:
            return "Warm"
        else:
            return "Hot"

    df["temp_type"] = df["eq_temp"].apply(temp_bucket)

    return df


df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("Filters")

# year range
min_year = int(df["year"].min())
max_year = int(df["year"].max())

year_range = st.sidebar.slider(
    "Discovery Year",
    min_year, max_year,
    (min_year, max_year)
)

# method
methods = st.sidebar.multiselect(
    "Discovery Method",
    options=sorted(df["method"].dropna().unique()),
    default=sorted(df["method"].dropna().unique())
)

# size
sizes = st.sidebar.multiselect(
    "Planet Size",
    options=sorted(df["size_type"].unique()),
    default=sorted(df["size_type"].unique())
)

# temperature
temps = st.sidebar.multiselect(
    "Temperature Class",
    options=sorted(df["temp_type"].unique()),
    default=sorted(df["temp_type"].unique())
)

# distance
max_dist = float(np.nanpercentile(df["distance_pc"], 95))
dist_range = st.sidebar.slider(
    "Distance (parsec)",
    0.0, float(df["distance_pc"].max()),
    (0.0, max_dist)
)

# ---------------- APPLY FILTERS ----------------
filtered = df[
    (df["year"].between(year_range[0], year_range[1])) &
    (df["method"].isin(methods)) &
    (df["size_type"].isin(sizes)) &
    (df["temp_type"].isin(temps)) &
    (df["distance_pc"].between(dist_range[0], dist_range[1]))
]

# ---------------- HEADER ----------------
st.title("Exoplanet Discovery Dashboard")

# ---------------- KPI ROW ----------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Planets", len(filtered))
c2.metric("Stars", filtered["star"].nunique())
c3.metric("Methods", filtered["method"].nunique())
c4.metric("Avg Distance (pc)", round(filtered["distance_pc"].mean(), 1))

# ---------------- CHARTS ----------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Discoveries by Year")
    year_chart = (
        filtered.groupby("year")
        .size()
        .reset_index(name="count")
        .sort_values("year")
    )
    st.line_chart(year_chart.set_index("year"))

with col2:
    st.subheader("Discovery Methods")
    method_chart = (
        filtered["method"]
        .value_counts()
        .reset_index()
    )
    method_chart.columns = ["method", "count"]
    st.bar_chart(method_chart.set_index("method"))

# ---------------- SIZE + TEMP ----------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("Planet Size Types")
    size_chart = (
        filtered["size_type"]
        .value_counts()
        .reset_index()
    )
    size_chart.columns = ["size", "count"]
    st.bar_chart(size_chart.set_index("size"))

with col4:
    st.subheader("Temperature Classes")
    temp_chart = (
        filtered["temp_type"]
        .value_counts()
        .reset_index()
    )
    temp_chart.columns = ["temp", "count"]
    st.bar_chart(temp_chart.set_index("temp"))

# ---------------- RELATIONSHIP ----------------
st.subheader("Mass vs Radius")

scatter_df = filtered[["mass_earth", "radius_earth"]].dropna()

st.scatter_chart(
    scatter_df,
    x="mass_earth",
    y="radius_earth"
)

# ---------------- DATA VIEW ----------------
with st.expander("View Cleaned Data"):
    st.dataframe(filtered, use_container_width=True)
