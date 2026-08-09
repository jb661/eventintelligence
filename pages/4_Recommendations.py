import streamlit as st
import streamlit.components.v1 as components

st.title("Our recommendations")
st.write("We suggest two possible strategies:")

strat_1, strat_2 = st.columns(2)

with strat_1:
    with st.container(border=True):
        st.markdown("## Strategy 1")
        st.markdown("### Avoid London for less perfomed but still popular shows")
        st.markdown("There exists genres like Blues, Jazz, R&B and Reggae that remain popular but don't have a lot of demand outside London. Recent census statistics [show](https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/bulletins/populationestimatesforenglandandwales/mid2025#regions) that the east of England has mantained population (in contrast to other parts of the UK). This represents a market opportunity for these genres.")

with strat_2:
    with st.container(border=True):
        st.markdown("## Strategy 2")
        st.markdown("### High risk high reward")
        st.markdown("There are genres that are severly underserved and there is practically no competition. These include Holiday, Latin and New Age music. We recommend avoiding genres like Chanson Francaise and Ballads, as our analysis indicates the risk is simply too high. If this strategy is pursued, we recommend doing further research to understand the demand. It could very well be that there is appetite for New Age music in Norwich...")

st.markdown("---")


