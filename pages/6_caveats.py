import streamlit as st
# import streamlit.components.v1 as components

st.title("Caveats")

col_1, col_2, col_3 = st.columns(3)
with col_1:
    with st.container(border=True):
        st.markdown("### 📅 **1. Listed ≠ Scheduled**")
        st.markdown(
            "The API returns announced events only. Apparent sparsity in later months "
            "is an artefact of the onsale calendar, not a seasonal lull."
        )
with col_2:
    with st.container(border=True):
        st.markdown("### 📊 **2. Baseline is Internal**")
        st.markdown(
            "LQ compares each city against the national average *within this pull*, "
            "not against GB live music overall."
        )
with col_3:
    with st.container(border=True):
        st.markdown("### ⚠️ **3. Truncation**")
        st.markdown(
            "Any window flagged in `log_df` hit the record ceiling and is incomplete; "
            "those weeks would need re-fetching at daily granularity."
        )
col_4, col_5= st.columns(2)
with col_4:
    with st.container(border=True):
        st.markdown("### 📉 **4. Small Samples**")
        st.markdown(
            "Most cities carry too few acts for a stable LQ. The `min_acts` floor "
            "is a visible guard, not a fix."
        )
with col_5:
    with st.container(border=True):
        st.markdown("### 🎟️ **5. No Price Data**")
        st.markdown(
            "`priceRanges` is not exposed to this API key, so the analysis cannot "
            "distinguish a £15 club show from a £60 arena date. A genre can look thin "
            "in a city while being thin only at a scale the act does not play."
        )

col_6, col_7 = st.columns(2)
with col_6:
    with st.container(border=True):
        st.markdown("### 🏛️ **6. Venue Identity**")
        st.markdown(
            "Ticketmaster sometimes carries more than one `venue_id` for the same physical "
            "room after a rebrand, which inflates venue counts and deflates acts-per-venue."
        )
with col_7:
    with st.container(border=True):
        st.markdown("### 💡 **7. Underserved ≠ Opportunity**")
        st.markdown(
            "A low LQ identifies a gap. Gaps need a demand-side explanation before "
            "they become recommendations — ONS population normalisation is the "
            "cheapest partial check."
        )

