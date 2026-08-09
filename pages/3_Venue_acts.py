import streamlit as st
import streamlit.components.v1 as components

from Home import apply_theme

apply_theme("Tableau dashboard")

VIZ_W, VIZ_H = 1000, 827

TABLEAU_URL = (
    "https://public.tableau.com/views/EventIntelligenceWorkbook/Dashboard1"
    "?:language=en-GB&:embed=y"
)

st.title("Venue activity map")
st.caption(
    "Circle size is distinct acts hosted per venue, not venue capacity. "
    "Published snapshot — re-running the notebook does not update this view."
)

components.html(
    f"""
    <script type="module"
      src="https://public.tableau.com/javascripts/api/tableau.embedding.3.latest.min.js">
    </script>
    <tableau-viz
        src="{TABLEAU_URL}"
        toolbar="bottom"
        hide-tabs
        width="{VIZ_W}"
        height="{VIZ_H}">
    </tableau-viz>
    """,
    height=VIZ_H + 60,
    width=VIZ_W + 20,
)
st.info("London saturates the market a lot regardless of genre. Emerging markets are the east, the south west and the north east of England, with Wales closely behind.")
if st.button("Go to Genre Population"):
    st.switch_page("pages/4_Genre_Population.py")
