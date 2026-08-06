from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

LOGO = Path(__file__).parent / "assets" / "eventintelligence-logo.png"

st.set_page_config(
    page_title="Vantage Talent — Market Analysis",
    page_icon=str(LOGO),
    layout="wide",
)

# Pins the logo to the top-left of every page and the sidebar.
st.logo(str(LOGO), size="large")


@st.cache_data
def load():
    return pd.read_csv("data/events.csv", parse_dates=["event_date"])


clean = load()

col_logo, col_title = st.columns([1, 6], vertical_alignment="center")
with col_logo:
    st.image(str(LOGO), width=140)
with col_title:
    st.title("Welcome!")
    st.caption(f"Data fetched {clean['fetched_at'].iloc[0]} · {len(clean):,} events")

if st.button("Reload data"):
    st.cache_data.clear()
    st.rerun()