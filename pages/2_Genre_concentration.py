import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Genre concentration", layout="wide")
st.title("Genre concentration by UK market")

@st.cache_data
def load():
    df = pd.read_csv("data/events.csv", parse_dates=["event_date"])
    return df

clean = load()
st.caption(f"Fetched {clean['fetched_at'].iloc[0]} · {len(clean):,} events")

# Analysis bases — same logic as the notebook
known = clean[clean["genre"].notna() & (clean["genre"] != "Other")]
base = known.dropna(subset=["attraction_id"])
local = base.drop_duplicates(subset=["attraction_id", "city"])
national = base.drop_duplicates(subset="attraction_id")

col1, col2 = st.columns([2, 1])
with col1:
    genre = st.selectbox("Genre", sorted(national["genre"].unique()))
with col2:
    min_acts = st.slider("Minimum acts in city", 5, 100, 20)

nat_share = (national["genre"] == genre).mean()

lq = local.groupby("city").agg(
    genre_acts=("genre", lambda g: (g == genre).sum()),
    total_acts=("genre", "size"),
)
lq["lq"] = (lq["genre_acts"] / lq["total_acts"] / nat_share).round(2)
lq = lq[lq["total_acts"] >= min_acts].reset_index()

if lq.empty:
    st.warning(f"No cities have {min_acts}+ acts. Lower the threshold.")
    st.stop()

lq["direction"] = lq["lq"].apply(lambda x: "Over-served" if x > 1 else "Underserved")
lq["label"] = lq["city"] + " (" + lq["total_acts"].astype(str) + ")"

st.metric(f"National {genre} share", f"{nat_share:.1%}",
          help="Share of all acts in this pull classified as this genre")

fig = px.bar(
    lq.sort_values("lq"),
    x="lq", y="label", orientation="h",
    color="direction",
    color_discrete_map={"Underserved": "#00B4C8", "Over-served": "#1A3A8F"},
    hover_data={"genre_acts": True, "total_acts": True, "lq": ":.2f",
                "label": False, "direction": False},
    labels={"lq": "Location quotient", "label": ""},
)
fig.add_vline(x=1, line_dash="dash", line_color="grey")
fig.update_layout(height=max(400, 26 * len(lq)), showlegend=True,
                  legend_title_text="")

st.plotly_chart(fig, use_container_width=True)
st.caption("LQ = city's share of this genre ÷ national share. "
           "Act counts in brackets — below ~10, a single booking swings the ratio.")

with st.expander("Underlying figures"):
    st.dataframe(lq[["city", "genre_acts", "total_acts", "lq"]]
                 .sort_values("lq"), use_container_width=True)