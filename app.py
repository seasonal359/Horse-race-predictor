# Streamlit App using rp_us scraper

import streamlit as st
import pandas as pd
from datetime import datetime
from rp_us import get_race_links, get_race_horses, TRACK_CODES

st.set_page_config(page_title="🏇 US Race Predictor Debug", layout="wide")
st.title("🏇 US Thoroughbred Race Scraper (Racing Post)")

st.markdown("""
This app pulls **live racecards** from [RacingPost.com](https://www.racingpost.com) using a custom U.S. track scraper.
Use the dropdown to choose a track and date, then see horses + odds.
""")

# --- Sidebar Options ---
today_str = datetime.today().strftime("%Y-%m-%d")
st.sidebar.header("Race Selection")
race_date = st.sidebar.text_input("Race Date (YYYY-MM-DD)", value=today_str)
track_name = st.sidebar.selectbox("Select U.S. Track", list(TRACK_CODES.keys()))

# --- Fetch Races ---
races = get_race_links(track_name, race_date)
if not races:
    st.error(f"❌ No races found for {track_name} on {race_date}.")
    st.stop()

race_labels = [f"{r[1]} - {r[0]}" for r in races]  # time - race name
selected_label = st.sidebar.selectbox("Choose Race", race_labels)

if selected_label:
    selected_index = race_labels.index(selected_label)
    race_name, race_time, race_url = races[selected_index]
    st.subheader(f"📍 {track_name} | {race_name} | {race_time}")
    st.write(f"[🔗 View on Racing Post]({race_url})")

    horses = get_race_horses(race_url)
    if not horses:
        st.warning("No horses returned for this race.")
    else:
        df = pd.DataFrame(horses)
        st.dataframe(df, use_container_width=True)
