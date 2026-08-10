import streamlit as st

from Home import apply_theme, bases, load

apply_theme("Recommendations")

# --- Scope -------------------------------------------------------------------
# Genre fixed here rather than exposed as a control: the brief asks for a
# documented choice, made early. Change this one line to re-run the page
# against a different genre.
GENRE = "R&B"

MIN_SCENE = 20      # a city needs this many acts overall before its LQ is read
MIN_GENRE_ACTS = 5  # and this many of the genre before the ratio is stable
LQ_LOW, LQ_HIGH = 0.4, 0.7   # the band where a gap is real but the genre works
N_NEAR = 4                   # nearby markets used for the regional demand signal
OVER = 1.2          # above this, the city over-programmes the genre

clean = load()
frames = bases()
local, national = frames["local"], frames["national"]

nat_share = (national["genre"] == GENRE).mean()

st.title(f"Where a mid-tier {GENRE} act should tour")
st.caption(f"Data fetched {clean['fetched_at'].iloc[0]} · {len(clean):,} events")

# --- Calculation -------------------------------------------------------------
lq = local.groupby("city").agg(
    genre_acts=("genre", lambda s: (s == GENRE).sum()),
    total_acts=("genre", "size"),
)
lq["lq"] = (lq["genre_acts"] / lq["total_acts"] / nat_share).round(2)

venues = (clean.dropna(subset=["venue_id", "city"])
          .groupby("city")["venue_id"].nunique().rename("venues"))
lq = lq[lq["total_acts"] >= MIN_SCENE].join(venues).reset_index()

if lq.empty:
    st.warning(f"No cities carry {MIN_SCENE}+ acts. Lower MIN_SCENE.")
    st.stop()

core = lq[(lq["genre_acts"] >= MIN_GENRE_ACTS)
          & (lq["lq"].between(LQ_LOW, LQ_HIGH))].sort_values("total_acts", ascending=False)
watch = lq[(lq["genre_acts"] < MIN_GENRE_ACTS)
           & (lq["lq"] < LQ_HIGH) & (lq["genre_acts"] > 0)].sort_values("total_acts", ascending=False)
over = lq[(lq["lq"] > OVER)
          & (lq["genre_acts"] >= MIN_GENRE_ACTS)].sort_values("total_acts", ascending=False)

# --- Scope note --------------------------------------------------------------
with st.container(border=True):
    st.markdown(f"### Why {GENRE}")
    st.markdown(
        f"{GENRE} accounts for **{nat_share:.1%}** of acts nationally and appears "
        f"across **{int((lq['genre_acts'] > 0).sum())} of the {len(lq)} cities** big "
        "enough to score. It is a genre with a clear national profile that "
        "concentrates heavily in one market, which is exactly the shape the brief "
        "asks us to interrogate."
    )
    st.markdown(
        "We ruled out Rock, which is 45% of the pull and functions as a catch-all "
        "rather than a genre. We ruled out Pop because Ticketmaster files most pop "
        "acts under Rock, leaving its baseline understated fourfold. And we ruled "
        "out Jazz, where 79% of listings are London and the second city carries "
        "four acts."
    )
    st.caption(
        f"Trade-off worth stating: only {int((lq['genre_acts'] >= MIN_GENRE_ACTS).sum())} "
        f"cities carry {MIN_GENRE_ACTS}+ {GENRE} acts, so the shortlist is short. "
        "Route B below is where most of the map sits, and it is thinner evidence."
    )

# --- Strategies --------------------------------------------------------------
st.markdown("---")
st.subheader("Two routes, depending on appetite for risk")

strat_1, strat_2 = st.columns(2)

with strat_1:
    with st.container(border=True):
        st.markdown("## Route A — big scenes, under-programmed")
        st.markdown(f"### {', '.join(core.head(4)['city'].tolist()) or 'None qualifying'}")
        st.markdown(
            f"Cities running {MIN_GENRE_ACTS}+ {GENRE} acts but at a rate below the "
            "national average. Promoters already book the genre, so the rooms and "
            "the relationships exist. The gap is in how much they programme, not "
            "whether they programme it at all. Lower risk, and the LQ rests on "
            "enough acts to be stable."
        )

with strat_2:
    with st.container(border=True):
        st.markdown("## Route B — thinner markets, sharper gaps")
        st.markdown(f"### {', '.join(watch.head(4)['city'].tolist()) or 'None qualifying'}")
        st.markdown(
            f"Lower quotients, but each rests on fewer than {MIN_GENRE_ACTS} acts. "
            "One booking moves these numbers materially, so they are leads to check "
            "with a local promoter rather than conclusions. Worth a call if you are "
            "already routing nearby."
        )

# --- Avoid -------------------------------------------------------------------
st.markdown("---")
with st.container(border=True):
    st.markdown("## Where not to lead")
    if len(over):
        names = ", ".join(f"**{r.city}** (LQ {r.lq})" for r in over.head(4).itertuples())
        st.markdown(
            f"{names} already book more {GENRE} than their scene size predicts. A "
            "developing act competes for those slots against better-established "
            "names, on nights that are already full. Not unplayable, but not where "
            "a limited budget goes first."
        )
    else:
        st.markdown(f"No city materially over-indexes on {GENRE} in this pull.")

# --- Regional demand signal --------------------------------------------------
# The nearest scored markets that book the genre at all. Where those neighbours
# sit at or above the national rate, the regional audience is demonstrated and
# the shortlisted city is the one under-programming it. Straight-line distance
# on mean venue coordinates: close enough at UK scale, not a routing tool.
coords = (clean.dropna(subset=["latitude", "longitude"])
          .groupby("city")[["latitude", "longitude"]].mean())

def regional_signal(city):
    if city not in coords.index:
        return None, []
    la, lo = coords.loc[city]
    d = ((coords["latitude"] - la) ** 2 + (coords["longitude"] - lo) ** 2) ** 0.5
    near = d[d.index.isin(lq["city"])].sort_values().index[1:N_NEAR + 1]
    rows = lq[lq["city"].isin(near) & (lq["genre_acts"] > 0)]
    return (rows["lq"].mean() if len(rows) else None), rows

if len(core):
    scored = [(c, regional_signal(c)[0]) for c in core["city"]]
    scored = [(c, v) for c, v in scored if v is not None]
    pick_city = max(scored, key=lambda t: t[1])[0] if scored else core.iloc[0]["city"]
    pick = core[core["city"] == pick_city].iloc[0]
    signal, neighbours = regional_signal(pick_city)

    st.markdown("---")
    with st.container(border=True):
        st.markdown(f"## \u2705 Start with {pick['city']}")
        st.markdown(
            f"{pick['city']} runs **{int(pick['total_acts'])} acts across "
            f"{int(pick['venues'])} venues**, of which **{int(pick['genre_acts'])} "
            f"are {GENRE}** \u2014 a quotient of **{pick['lq']:.2f}**, roughly "
            f"{1 - pick['lq']:.0%} below the national rate."
        )
        if signal is not None and len(neighbours):
            nb = ", ".join(
                f"{r.city} ({r.lq:.2f})" for r in neighbours.itertuples()
            )
            st.markdown(
                f"**Why here rather than the other two.** The nearest markets that "
                f"book {GENRE} at all \u2014 {nb} \u2014 average **{signal:.2f}**, at or "
                f"above the national rate. The regional audience is already "
                f"demonstrated; {pick['city']} is the city under-programming it. "
                "That is the closest this data comes to evidence of demand rather "
                "than absence, and those neighbours sit close enough to route "
                "together on a limited budget."
            )
            st.caption(
                "The other shortlisted cities score lower on the same measure: "
                + "; ".join(f"{c} {v:.2f}" for c, v in sorted(scored, key=lambda t: -t[1])
                            if c != pick_city)
            )
        st.markdown(
            "**Before committing:** we can see supply, not sales. Confirm with one "
            "promoter that the gap reflects programming rather than a room that has "
            "already tried. A support slot or a midweek date is a cheaper test than "
            "a routed run."
        )

if st.button("Go to caveats"):
    st.switch_page("pages/6_Caveats.py")