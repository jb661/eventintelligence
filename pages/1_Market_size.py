import plotly.express as px
import streamlit as st

from Home import PALETTE as C, apply_theme, bases, brand_layout, load

apply_theme("Acts by city")

clean = load()
local = bases()["local"]
genre_list = sorted(local['genre'].unique())


# Reserved so the heading can name the selected genre, which isn't known
# until the selectbox below has run.
title_slot = st.empty()
st.caption(f"Data fetched {clean['fetched_at'].iloc[0]} · {len(clean):,} events")

col1, col2 = st.columns([2, 1])
with col1:
    genre = st.selectbox("Genre", genre_list)
with col2:
    top_n = st.slider("Cities to show", 5, 40, 20)

title_slot.title(f"{genre} acts by city")

g = local[local["genre"] == genre]
counts = g.groupby("city").size().sort_values(ascending=False)
d = counts.head(top_n).to_frame("acts").reset_index()
d["pct_of_national"] = (d["acts"] / len(g) * 100).round(1)
d["cumulative"] = d["pct_of_national"].cumsum().round(1)

c1, c2, c3 = st.columns(3)
c1.metric(f"{genre} acts nationally", f"{len(g):,}")
c2.metric("Top 3 cities hold", f"{counts.head(3).sum() / len(g):.0%}")
c3.metric("Cities with 5+ acts", f"{(counts >= 5).sum()} of {len(counts)}")

plot_d = d.sort_values("acts")
lead_city = plot_d["city"].iloc[-1]
bar_colours = [C["accent"] if city == lead_city else C["primary"] for city in plot_d["city"]]

fig = px.bar(
    plot_d,
    x="acts", y="city", orientation="h",
    text="acts",
    hover_data={"pct_of_national": ":.1f", "cumulative": ":.1f", "acts": False},
    labels={"acts": f"Distinct {genre} acts", "city": ""},
)
fig.update_traces(marker_color=bar_colours, textposition="outside")
brand_layout(fig, len(plot_d))
fig.update_xaxes(range=[0, plot_d["acts"].max() * 1.12])
st.plotly_chart(fig, use_container_width=True)
st.caption(
    "Counts are distinct acts, not events — a three-night run counts once. "
    f"{lead_city} leads."
)
st.markdown("---")
# I've made a cutoff of 30 events whose top three is below 55%
# This can easily be changed but seems sensible
if len(g) < 30:
    st.info(f"There isn't a lot of demand for {genre}")
elif counts.head(3).sum()/len(g) < .5 :
    st.info(f"There doesn't seem to be a gap in the market for {genre} music")
else:
    st.info(f"It is worth it to keep an eye on {genre} music")


if st.button("Go to concentration by city"):
    st.switch_page("pages/2_Genre_concentration.py")
