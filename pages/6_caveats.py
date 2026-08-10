from pathlib import Path

import pandas as pd
import streamlit as st

from Home import apply_theme, bases

apply_theme("Caveats")

LOG_FILE = Path(__file__).parent.parent / "data" / "processed" / "ingestion_log.csv"

local = bases()["local"]
n_reliable = int((local.groupby("city").size() >= 10).sum())
n_cities = int(local["city"].nunique())

try:
    log = pd.read_csv(LOG_FILE)
    n_trunc, n_windows = int(log["truncated"].sum()), len(log)
except FileNotFoundError:
    n_trunc, n_windows = None, None

st.title("What this can't tell you")

with st.container(border=True):
    st.markdown("### 📅 A skew to the earlier months")
    st.markdown(
        "Ticketmaster only lists shows that are on sale. Tours get announced three "
        "to six months ahead, so the back end of our window will always look "
        "emptier. That dropoff means that our analysis will be skewed to the early months."
    )

with st.container(border=True):
    st.markdown("### 💡 A gap isn't proof of an opportunity")
    st.markdown(
        "A low quotient means a city books less of a genre than the country does. "
        "It can't tell us whether nobody has tried, or whether people tried and it "
        "didn't sell. Every 'underserved' city here is a question for a local promoter to "
        "answer at the city level."
    )

st.markdown("---")
st.subheader("Further limitations")

col_1, col_2, col_3 = st.columns(3)

with col_1:
    with st.container(border=True):
        st.markdown("### 🙋 Nothing measures demand")
        st.markdown(
            "Everything here counts supply: acts booked, venues used, shows listed. "
            "None of it knows how many and at what price tickets sold."
        )

with col_2:
    with st.container(border=True):
        st.markdown("### 🎟️ No ticket prices")
        st.markdown(
            "Ticketmaster doesn't expose pricing on a public key. We tested it four "
            "ways. A £15 club night and a £60 arena show look identical to us."
        )

with col_3:
    with st.container(border=True):
        st.markdown("### 📊 Relative to this pull only")
        st.markdown(
            "Over-indexed means over-indexed against the events we collected, not "
            "against UK live music. Anything ticketed elsewhere is invisible, and "
            "that's much of the grassroots end."
        )

col_4, col_5, col_6 = st.columns(3)

with col_4:
    with st.container(border=True):
        st.markdown("### 📉 Small cities are noise")
        st.markdown(
            f"Only **{n_reliable} of {n_cities} cities** have ten or more acts. "
            "Below that, one booking moves the ratio enough to look like a trend."
        )

with col_5:
    with st.container(border=True):
        st.markdown("### ⚠️ Busy weeks may be clipped")
        if n_trunc is None:
            body = ("Ticketmaster caps a query at 1,000 records, so we pulled week "
                    "by week. The ingestion log records which windows came close.")
        elif n_trunc == 0:
            body = (f"Ticketmaster caps a query at 1,000 records, so we pulled week "
                    f"by week. **None of the {n_windows} windows hit the cap.**")
        else:
            body = (f"Ticketmaster caps a query at 1,000 records. **{n_trunc} of our "
                    f"{n_windows} weekly windows** hit it, so those weeks are "
                    "undercounted.")
        st.markdown(body)

with col_6:
    with st.container(border=True):
        st.markdown("### 🏛️ One room can appear twice")
        st.markdown(
            "Venues get rebranded and the old listing doesn't always get merged. "
            "Where that happens we count one room as two, and competition for slots "
            "looks softer than it is."
        )