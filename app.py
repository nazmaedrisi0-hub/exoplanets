import streamlit as st
import pandas as pd
import numpy as np

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Exoplanet Analytics",
    page_icon="🪐",
    layout="wide"
)

# ---------------- LIGHT STYLE ----------------
st.markdown("""
<style>
.main {
    background-color: #f7f9fc;
}
.block-container {
    padding-top: 2rem;
}
h1, h2, h3 {
    color: #1f2c56;
}
[data-testid="metric-container"] {
    background: white;
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("exoplanets.csv")

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

    num_cols = [
        "orbital_period", "semi_major_axis", "radius_earth", "mass_earth",
        "eccentricity", "insolation", "eq_temp", "star_temp",
        "star_radius", "star_mass", "metallicity", "distance_pc"
    ]

    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # size buckets
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

    # temp buckets
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
st.sidebar.header("🧭 Filters")

min_year = int(df["year"].min())
max_year = int(df["year"].max())

year_range = st.sidebar.slider(
    "Discovery Year",
    min_year, max_year,
    (min_year, max_year)
)

methods = st.sidebar.multiselect(
    "Method",
    sorted(df["method"].dropna().unique()),
    sorted(df["method"].dropna().unique())
)

sizes = st.sidebar.multiselect(
    "Planet Size",
    sorted(df["size_type"].unique()),
    sorted(df["size_type"].unique())
)

temps = st.sidebar.multiselect(
    "Temperature",
    sorted(df["temp_type"].unique()),
    sorted(df["temp_type"].unique())
)

# ---------------- FILTER ----------------
filtered = df[
    (df["year"].between(year_range[0], year_range[1])) &
    (df["method"].isin(methods)) &
    (df["size_type"].isin(sizes)) &
    (df["temp_type"].isin(temps))
]

# ---------------- TITLE ----------------
st.title("🪐 Exoplanet Discovery Dashboard")
st.caption("Interactive exploration of planetary discoveries")

# ---------------- KPI ----------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("🪐 Total Planets", len(filtered))
c2.metric("⭐ Host Stars", filtered["star"].nunique())
c3.metric("🔭 Methods", filtered["method"].nunique())
c4.metric("📏 Avg Distance (pc)", round(filtered["distance_pc"].mean(), 1))

st.divider()

# ---------------- CHARTS ----------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Discoveries Over Time")
    year_chart = (
        filtered.groupby("year")
        .size()
        .reset_index(name="count")
        .sort_values("year")
    )
    st.line_chart(year_chart.set_index("year"))

with col2:
    st.subheader("🧪 Discovery Methods")
    method_chart = (
        filtered["method"]
        .value_counts()
        .reset_index()
    )
    method_chart.columns = ["method", "count"]
    st.bar_chart(method_chart.set_index("method"))

st.divider()

# ---------------- SIZE + TEMP ----------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("🌍 Planet Size Distribution")
    size_chart = (
        filtered["size_type"]
        .value_counts()
        .reset_index()
    )
    size_chart.columns = ["size", "count"]
    st.bar_chart(size_chart.set_index("size"))

with col4:
    st.subheader("🌡 Temperature Classes")
    temp_chart = (
        filtered["temp_type"]
        .value_counts()
        .reset_index()
    )
    temp_chart.columns = ["temp", "count"]
    st.bar_chart(temp_chart.set_index("temp"))

st.divider()

# ---------------- RELATIONSHIP ----------------
st.subheader("⚖ Mass vs Radius")

scatter_df = filtered[["mass_earth", "radius_earth"]].dropna()

st.scatter_chart(
    scatter_df,
    x="mass_earth implying y="radius_earth"
)

# ---------------- DATA ----------------
with st.expander("📄 View Dataset"):
    st.dataframe(filtered, use_container_width=True)
