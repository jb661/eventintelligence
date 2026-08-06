import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Where the genre plays", layout="wide")
st.title("Where the genre plays")

@st.cache_data
def load():
    return pd.read_csv("data/events.csv", parse_dates=["event_date"])

clean = load()
st.caption(f"Data fetched {clean['fetched_at'].iloc[0]} · {len(clean):,} events")

known = clean[clean["genre"].notna() & (clean["genre"] != "Other")]
base = known.dropna(subset=["attraction_id"])
local = base.drop_duplicates(subset=["attraction_id", "city"])

col1, col2 = st.columns([2, 1])
with col1:
    genre = st.selectbox("Genre", sorted(local["genre"].unique()))
with col2:
    top_n = st.slider("Cities to show", 5, 40, 20)

g = local[local["genre"] == genre]
counts = g.groupby("city").size().sort_values(ascending=False)

d = counts.head(top_n).to_frame("acts").reset_index()
d["pct_of_national"] = (d["acts"] / len(g) * 100).round(1)
d["cumulative"] = d["pct_of_national"].cumsum().round(1)

c1, c2, c3 = st.columns(3)
c1.metric(f"{genre} acts nationally", f"{len(g):,}")
c2.metric("Top 3 cities hold", f"{counts.head(3).sum() / len(g):.0%}")
c3.metric("Cities with 5+ acts", f"{(counts >= 5).sum()} of {len(counts)}")

fig = px.bar(
    d.sort_values("acts"),
    x="acts", y="city", orientation="h",
    text="acts",
    hover_data={"pct_of_national": ":.1f", "cumulative": ":.1f", "acts": False},
    labels={"acts": f"Distinct {genre} acts", "city": ""},
)
fig.update_traces(marker_color="#1A3A8F", textposition="outside")
fig.update_xaxes(range=[0, d["acts"].max() * 1.12])
fig.update_layout(height=max(400, 26 * len(d)))

st.plotly_chart(fig, use_container_width=True)
st.caption("Counts are distinct acts, not events — a three-night run counts once.")

with st.expander("All cities"):
    st.dataframe(counts.to_frame("acts"), use_container_width=True)