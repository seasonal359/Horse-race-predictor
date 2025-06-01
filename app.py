import streamlit as st
from rpscrape.rp import RP
import pandas as pd

st.title("🏇 Horse Race Predictor - Debug Mode")

st.markdown("### 🔍 Pulling data from rpscrape...")

rp = RP()
cards = rp.get_racecards()

# Debug: Show all raw cards returned
st.write("### Raw racecards from RP", cards)

if not cards:
    st.error("❌ No racecards returned by rpscrape. This means RP may not be publishing live U.S. data today, or the scraper is returning UK races.")
else:
    race_ids = [card["race_id"] for card in cards]
    selected = st.selectbox("Select a race", race_ids)

    if selected:
        race = rp.get_racecard(selected)
        st.markdown(f"### Race ID: {selected}")
        if "horses" in race:
            horses = race["horses"]
            df = pd.DataFrame(horses)
            st.dataframe(df)
        else:
            st.warning("No horses found in this race.")
