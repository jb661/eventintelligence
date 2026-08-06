import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Vantage Talent — Market Analysis", layout="wide")

@st.cache_data
def load():
    return pd.read_csv("data/events.csv", parse_dates=["event_date"])

clean = load()

st.title("Welcome!")
st.caption(f"Data fetched {clean['fetched_at'].iloc[0]} · {len(clean):,} events")

if st.button("Reload data"):
    st.cache_data.clear()
    st.rerun()