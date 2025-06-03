
# 🇺🇸 US Thoroughbred Race Viewer (Racing API) - Stable Version

import streamlit as st
import requests
import base64
import datetime
import pandas as pd

# --- Helper: Build Auth Header from Streamlit Secrets ---
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")
if not username or not password:
    st.error("Missing API credentials in Streamlit secrets.")
    st.stop()

basic_auth = f"{username}:{password}"
auth_header = base64.b64encode(basic_auth.encode()).decode()
headers = {
    "Authorization": f"Basic {auth_header}"
}

# --- Get Meets ---
def fetch_meets(date_str):
    url = f"https://api.theracingapi.com/v1/north-america/meets?date={date_str}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch meets: {response.status_code} - {response.text}")
        return []
    return response.json().get("meets", [])

# --- Get Entries for a Meet ---
def fetch_entries(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/entries"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch entries: {response.status_code} - {response.text}")
        return []
    return response.json().get("races", [])

# --- Streamlit App ---
st.title("🇺🇸 US Thoroughbred Race Viewer (Racing API)")
st.markdown("This app fetches North American race meets and entries via The Racing API.")

# --- Select Date ---
date = st.date_input("Select Date", value=datetime.date.today())
date_str = date.strftime("%Y-%m-%d")

# --- Fetch and Select Track ---
st.markdown("🔍 Fetching race data from The Racing API...")
meets = fetch_meets(date_str)

if not meets:
    st.warning("No meets found for selected date.")
    st.stop()

track_options = {f"{meet.get('track_name', 'Unknown')} ({meet.get('country', 'N/A')})": meet for meet in meets}
selected_track_label = st.selectbox("Select Track", list(track_options.keys()))
selected_meet = track_options[selected_track_label]

# --- Display Basic Meet Info ---
st.subheader(f"📍 {selected_meet.get('track_name')} - 🗓 {selected_meet.get('date')}")
st.write(f"Meet ID: `{selected_meet.get('meet_id')}` | Country: `{selected_meet.get('country')}`")

# --- Fetch and Show Entries ---
if st.checkbox("Show Race Entries"):
    races = fetch_entries(selected_meet['meet_id'])
    if races:
        for race in races:
            st.markdown(f"### Race {race.get('number')}: {race.get('name', 'Unknown')}")
            if 'runners' in race:
                df = pd.DataFrame(race['runners'])
                cols = [col for col in ['number', 'horse', 'jockey', 'trainer', 'odds', 'position'] if col in df.columns]
                st.dataframe(df[cols])
            else:
                st.warning("No runners found for this race.")
    else:
        st.info("No race entries available.")
