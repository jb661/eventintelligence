"""Home page, and the single source of truth for theme + data loading.

Pages import from this file. Everything below the __main__ guard is the home
page itself and does not run on import.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

from get_data import run_ingestion

# --- Brand palette -----------------------------------------------------------
PRIMARY = "#1A3A8F"    # deep navy — structural / default bars
SECONDARY = "#6B35C8"  # mid purple — hover chrome, reference lines
ACCENT = "#00B4C8"     # teal — the highlight, used sparingly
DARK = "#0D1F5C"       # near-black navy — type and depth
LIGHT = "#C8B8F0"      # pale lavender — gridlines, subtle fills
NEUTRAL = "#F4F4F6"    # off-white — backgrounds

PALETTE = {
    "primary": PRIMARY,
    "secondary": SECONDARY,
    "accent": ACCENT,
    "dark": DARK,
    "light": LIGHT,
    "neutral": NEUTRAL,
}

# Translucent tints. Alpha rather than a flat hex, so they read correctly
# against both the light and dark app backgrounds.
GRID = "rgba(200, 184, 240, 0.35)"   # LIGHT at 35%
CARD = "rgba(0, 180, 200, 0.08)"     # ACCENT at 8%

LOGO = Path(__file__).parent / "assets" / "eventintelligence-logo.png"
DATA_FILE = Path(__file__).parent / "data" / "processed" / "clean_events.csv"


def apply_theme(page_title="Vantage Talent — Market Analysis"):
    """Page config, logo and header. Call as the first Streamlit command on a page."""
    st.set_page_config(page_title=page_title, page_icon=str(LOGO), layout="wide")
    st.logo(str(LOGO), size="large")
    st.markdown(
        f"""
        <div style="
            border-left: 5px solid {ACCENT};
            padding-left: 12px;
            margin-top: 1.5rem;
            margin-bottom: 1.2rem;
        ">
            <h2 style="
                margin: 0;
                color: {DARK};
                font-size: 1.5rem;
                font-weight: 700;
                letter-spacing: -0.5px;
            ">
                {page_title}
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )


def brand_layout(fig, n_rows):
    """Apply the shared palette to a Plotly figure.

    Backgrounds stay transparent and text colour is left unset so the chart
    inherits whichever theme is active. The palette colours the data only.
    """
    fig.update_traces(
        hoverlabel=dict(bgcolor=SECONDARY, font_color=NEUTRAL, bordercolor=SECONDARY)
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID)
    fig.update_yaxes(showgrid=False)
    fig.update_layout(
        height=max(400, 26 * n_rows),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=30, t=20, b=40),
    )
    return fig


@st.cache_data
def load():
    return pd.read_csv(DATA_FILE, parse_dates=["event_date"])


@st.cache_data
def bases():
    """Analysis bases — same logic as the notebook."""
    clean = load()
    known = clean[clean["genre"].notna() & (clean["genre"] != "Other")]
    base = known.dropna(subset=["attraction_id"])
    return {
        "local": base.drop_duplicates(subset=["attraction_id", "city"]),
        "national": base.drop_duplicates(subset="attraction_id"),
    }


# --- Home page ---------------------------------------------------------------
if __name__ == "__main__":
    apply_theme()
    clean = load()

    with st.container(border=True):
        col_logo, col_title = st.columns([1, 4], vertical_alignment="center")
        with col_title:
            st.title("Welcome!")
            st.caption(
                f"Data fetched {clean['fetched_at'].iloc[0]} · {len(clean):,} events"
            )
        with col_logo:
            st.image(str(LOGO), width="stretch")

    st.markdown("---")

    st.markdown(
        f"""
        <div style="
            border-left: 5px solid {ACCENT};
            background: {CARD};
            padding: 18px 22px;
            border-radius: 4px;
            margin-bottom: 1.5rem;
        ">
            <div style="
                font-size: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 1px;
                opacity: 0.7;
                margin-bottom: 6px;
            ">The question</div>
            <div style="font-size: 1.25rem; line-height: 1.5; font-weight: 500;">
                Which UK markets offer the most viable touring opportunity for a
                mid-tier act, based on the concentration and distribution of live
                music events by genre and geography?
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("How we approached it")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        with st.container(border=True):
            st.markdown("### 🎤 How many acts are there?")
            st.write("Click below for a breakdown on genres")
            if st.button("📊 See stats", use_container_width=True):
                st.switch_page("pages/1_Market_size.py")

    with col_b:
        with st.container(border=True):
            st.markdown("### 📈 How are acts distributed?")
            st.write("Click below for genre concentration")
            if st.button("🎯 See info", use_container_width=True):
                st.switch_page("pages/2_Genre_concentration.py")

    with col_c:
        with st.container(border=True):
            st.markdown("### 📍 Where do acts take place?")
            st.write("Click below for event location information")
            if st.button("🗺️ See locations", use_container_width=True):
                st.switch_page("pages/3_Venue_acts.py")

    if st.button("Reload data"):
        with st.spinner("Running data refresh — this pulls 26 weekly windows..."):
            run_ingestion()
            st.cache_data.clear()
        st.toast("Data refreshed successfully!", icon="✅")
        st.rerun()