import plotly.express as px
import streamlit as st
import pandas as pd

from Home import PALETTE as C, apply_theme, bases, brand_layout, load

# --- ONS Reference Population Data ---
ONS_POPULATION_DATA = {
    "London": 8908000, "Birmingham": 1144000, "Leeds": 812000, "Glasgow": 635000,
    "Sheffield": 584000, "Manchester": 553000, "Bradford": 546000, "Edinburgh": 526000,
    "Liverpool": 496000, "Bristol": 472000, "Cardiff": 372000, "Leicester": 368000,
    "Coventry": 345000, "Belfast": 345000, "Nottingham": 323000, "Newcastle": 300000,
    "Brighton": 277000, "Brighton and Hove": 277000, "Derby": 261000, "Hull": 260000,
    "Stoke-on-Trent": 258000, "Southampton": 253000, "Milton Keynes": 230000,
    "York": 210000, "Portsmouth": 208000, "Aberdeen": 200000, "Plymouth": 264000,
    "Reading": 174000, "Oxford": 162000, "Cambridge": 145000, "Norwich": 144000,
}

apply_theme("Market Saturation")

clean = load()
local = bases()["local"]

if local.empty:
    st.warning("No event data available.")
    st.stop()

genre_list = sorted(local["genre"].unique())

# Reserved header slot for selected genre
title_slot = st.empty()

# Safe timestamp extraction
fetched_time = clean["fetched_at"].iloc[0] if "fetched_at" in clean.columns and not clean.empty else "N/A"
st.caption(f"Data fetched {fetched_time} · {len(clean):,} events")

col1, col2 = st.columns([2, 1])
with col1:
    genre = st.selectbox("Genre", genre_list)
with col2:
    top_n = st.slider("Cities to show", 5, 25, 10)

title_slot.title(f"{genre} saturation by city")

# Filter data for selected genre
g = local[local["genre"] == genre]
total_acts = len(g)

# Early exit if no acts exist for the selected genre
if total_acts == 0:
    st.info(f"There isn't a lot of demand for {genre} (0 national acts found).")
    st.stop()

# Group by city to get distinct acts
counts = g.groupby("city").size().to_frame("unique_acts").reset_index()

# Map ONS population data
counts["population"] = counts["city"].map(ONS_POPULATION_DATA)

# Drop cities we don't have population data for to ensure accurate per 100k math
counts = counts.dropna(subset=["population"])

if counts.empty:
    st.warning("No population data available for the cities hosting these acts.")
    st.stop()

# Calculate Saturation (Acts per 100k residents)
counts["acts_per_100k"] = (counts["unique_acts"] / counts["population"]) * 100000

# Sort and slice for the chart
d = counts.sort_values("acts_per_100k", ascending=False).head(top_n)

# Display metrics
top_city = d.iloc[0]["city"]
top_sat = d.iloc[0]["acts_per_100k"]
avg_sat = d["acts_per_100k"].mean()

c1, c2, c3 = st.columns(3)
c1.metric(f"{genre} acts nationally", f"{total_acts:,}")
c2.metric("Highest Saturation", top_city)
c3.metric(f"{top_city} acts per 100k", f"{top_sat:.1f}")

# Plotting setup
plot_d = d.sort_values("acts_per_100k") # Ascending for Plotly horizontal bars
lead_city = plot_d["city"].iloc[-1]
bar_colours = [C["accent"] if city == lead_city else C["primary"] for city in plot_d["city"]]

fig = px.bar(
    plot_d,
    x="acts_per_100k",
    y="city",
    orientation="h",
    text="acts_per_100k",
    hover_data={"unique_acts": True, "population": True, "acts_per_100k": ":.1f"},
    labels={
        "acts_per_100k": f"{genre} acts per 100,000 residents",
        "city": "",
        "unique_acts": "Raw Act Count",
        "population": "City Population"
    },
)

# Format text to 1 decimal place and apply brand layout
fig.update_traces(
    marker_color=bar_colours,
    texttemplate='%{text:.1f}',
    textposition="outside"
)
brand_layout(fig, len(plot_d))

# Give x-axis 15% padding so outer labels don't get cut off
fig.update_xaxes(range=[0, plot_d["acts_per_100k"].max() * 1.15])
st.plotly_chart(fig, use_container_width=True)

st.caption(
    f"Saturation measures distinct {genre} acts relative to city population. "
    f"A higher number means more acts per resident. {lead_city} leads."
)
st.markdown("---")

# Market Insight Logic
if avg_sat < 0.5:
    st.info(f"{genre} is highly undersaturated in these markets. Opportunity for growth.")
elif top_sat > avg_sat * 2.5:
    st.info(f"{lead_city} is heavily skewed compared to the average market for {genre}.")
else:
    st.info(f"{genre} market saturation is relatively balanced across top cities.")

if st.button("Go to recommendations"):
    st.switch_page("pages/5_Recommendations.py")
