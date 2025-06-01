import streamlit as st
from rpscrape.rp import RP
import pandas as pd

st.title("🏇 Horse Race Predictor - UK/Global Debug Mode")
st.markdown("### 🔍 Pulling all available races from rpscrape...")

rp = RP()
cards = rp.get_racecards()

# Show all cards regardless of country
st.write("### Raw racecards from RP", cards)

if not cards:
    st.error("❌ No racecards found from rpscrape.")
else:
    # Show races with track + time
    race_options = [
        f"{card['meeting']} - {card['time']} - {card['race_id']}"
        for card in cards
    ]
    selected_label = st.selectbox("Select a race", race_options)

    if selected_label:
        # Extract race_id from label
        selected_id = selected_label.split(" - ")[-1]
        race = rp.get_racecard(selected_id)

        st.markdown(f"### Race Info for ID `{selected_id}`")

        if "horses" in race:
            df = pd.DataFrame(race["horses"])
            st.dataframe(df)
        else:
            st.warning("No horses found in this race.")
