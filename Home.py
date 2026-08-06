"""Home page, and the single source of truth for theme + data loading.

Pages import from this file. Everything below the __main__ guard is the home
page itself and does not run on import.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

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


def apply_theme(page_title="Vantage Talent — Market Analysis"):
    """Page config, logo and CSS. Call as the first Streamlit command on a page."""
    st.set_page_config(page_title=page_title, page_icon=str(LOGO), layout="wide")
    st.logo(str(LOGO), size="large")
    st.markdown(
        f"""
        <style>
          div[data-testid="stMetric"] {{
              background: {CARD};
              border-top: 3px solid {ACCENT};
              border-radius: 4px;
              padding: 14px 16px;
          }}
        </style>
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
    return pd.read_csv("data/events.csv", parse_dates=["event_date"])


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

    col_logo, col_title = st.columns([1, 6], vertical_alignment="center")
    with col_logo:
        st.image(str(LOGO), width=140)
    with col_title:
        st.title("Welcome!")
        st.caption(
            f"Data fetched {clean['fetched_at'].iloc[0]} · {len(clean):,} events"
        )

    if st.button("Reload data"):
        st.cache_data.clear()
        st.rerun()