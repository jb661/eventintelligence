import plotly.express as px
import streamlit as st

from Home import PALETTE as C, apply_theme, bases, brand_layout, load

apply_theme("Genre concentration")

clean = load()
frames = bases()
local, national = frames["local"], frames["national"]

# Reserved so the heading can name the selected genre, which isn't known
# until the selectbox below has run.
title_slot = st.empty()
st.caption(f"Fetched {clean['fetched_at'].iloc[0]} · {len(clean):,} events")

col1, col2 = st.columns([2, 1])
with col1:
    genre = st.selectbox("Genre", sorted(national["genre"].unique()))
with col2:
    min_acts = st.slider("Minimum acts in city", 5, 100, 20)

title_slot.title(f"{genre} concentration by UK market")

nat_share = (national["genre"] == genre).mean()
lq = local.groupby("city").agg(
    genre_acts=("genre", lambda s: (s == genre).sum()),
    total_acts=("genre", "size"),
)
lq["lq"] = (lq["genre_acts"] / lq["total_acts"] / nat_share).round(2)
lq = lq[lq["total_acts"] >= min_acts].reset_index()

if lq.empty:
    st.warning(f"No cities have {min_acts}+ acts. Lower the threshold.")
    st.stop()

lq["direction"] = lq["lq"].apply(lambda x: "Over-served" if x > 1 else "Underserved")
lq["label"] = lq["city"] + " (" + lq["total_acts"].astype(str) + ")"

st.metric(
    f"National {genre} share", f"{nat_share:.1%}",
    help="Share of all acts in this pull classified as this genre",
)

fig = px.bar(
    lq.sort_values("lq"),
    x="lq", y="label", orientation="h",
    color="direction",
    color_discrete_map={"Underserved": C["accent"], "Over-served": C["primary"]},
    hover_data={"genre_acts": True, "total_acts": True, "lq": ":.2f",
                "label": False, "direction": False},
    labels={"lq": "Location quotient", "label": ""},
)
fig.add_vline(x=1, line_dash="dash", line_color=C["secondary"])
brand_layout(fig, len(lq))
fig.update_layout(showlegend=True, legend_title_text="")
st.plotly_chart(fig, use_container_width=True)
st.markdown("We defined the LQ coefficien to be $$\\frac{C_g}{N_g}$$ where $C_g$ is the city's share of the genre $g$ and $N_g$ is the national share of said genre")
st.caption(
    "Act counts in brackets — below ~10, a single booking swings the ratio."
)

with st.expander("Underlying figures"):
    st.dataframe(
        lq[["city", "genre_acts", "total_acts", "lq"]].sort_values("lq"),
        use_container_width=True,
    )

st.info("It is interesting to compare R&B and Jazz here. Although it appears that R&B is underepresented, the figures suggest that the demand for R&B is being met. This is not the case with Jazz.")
if st.button("Go to event location information"):
    st.switch_page("pages/3_Venue_acts.py")
