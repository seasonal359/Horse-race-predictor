
# 🇺🇸 US Thoroughbred Race Viewer (Racing API) - Entries Only Debug Version

import streamlit as st
import requests
import base64
import datetime
import pandas as pd

# --- Auth ---
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")
if not username or not password:
    st.error("Missing API credentials in Streamlit secrets.")
    st.stop()

auth = f"{username}:{password}"
headers = {
    "Authorization": "Basic " + base64.b64encode(auth.encode()).decode()
}

# --- Fetch Meets ---
def fetch_meets(date_str):
    url = f"https://api.theracingapi.com/v1/north-america/meets?date={date_str}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch meets: {response.status_code} - {response.text}")
        return []
    return response.json().get("meets", [])

# --- Fetch Entries ---
def fetch_entries(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/entries"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch entries: {response.status_code} - {response.text}")
        return []
    return response.json().get("races", [])

# --- UI ---
st.title("🇺🇸 US Thoroughbred Race Viewer (Racing API)")
st.markdown("This app fetches North American race meets and entries via The Racing API.")

date = st.date_input("Select Date", value=datetime.date.today())
date_str = date.strftime("%Y-%m-%d")

meets = fetch_meets(date_str)
if not meets:
    st.warning("No meets found.")
    st.stop()

track_options = {f"{m['track_name']} ({m['country']})": m for m in meets}
track_label = st.selectbox("Select Track", list(track_options.keys()))
meet = track_options[track_label]

st.markdown(f"📍 {meet['track_name']} - 🗓 {meet['date']}")
st.markdown(f"Meet ID: `{meet['meet_id']}` | Country: `{meet['country']}`")

entries = fetch_entries(meet['meet_id'])
if not entries:
    st.info("No race entries available.")
else:
    for race in entries:
        race_number = race.get('race_number', 'Unknown')
        race_name = race.get('race_name', 'Unnamed Race')
        st.subheader(f"Race {race_number}: {race_name}")
        runners = race.get('runners', [])
        if runners:
            data = []
            for r in runners:
                data.append({
                    "Number": r.get("program_number", "N/A"),
                    "Horse": r.get("horse", {}).get("name", "N/A"),
                    "Jockey": r.get("jockey", {}).get("alias", "N/A"),
                    "Trainer": r.get("trainer", {}).get("alias", "N/A"),
                    "Odds": r.get("odds", {}).get("decimal", "N/A"),
                })
            st.dataframe(pd.DataFrame(data))
        else:
            st.write("No runners found.")
