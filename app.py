
# 🇺🇸 US Thoroughbred Race Viewer (Racing API) - Entries Only with Fallbacks

import streamlit as st
import requests
import base64
import datetime
import pandas as pd

# --- Auth Header ---
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")
if not username or not password:
    st.error("Missing API credentials in Streamlit secrets.")
    st.stop()

auth_header = base64.b64encode(f"{username}:{password}".encode()).decode()
headers = { "Authorization": f"Basic {auth_header}" }

# --- Fetch Meets ---
def fetch_meets(date_str):
    url = f"https://api.theracingapi.com/v1/north-america/meets?date={date_str}"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error(f"Meets fetch failed: {r.status_code} - {r.text}")
        return []
    return r.json().get("meets", [])

# --- Fetch Entries ---
def fetch_entries(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/entries"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error(f"Entries fetch failed: {r.status_code} - {r.text}")
        return []
    return r.json().get("races", [])

# --- App Interface ---
st.title("🇺🇸 US Thoroughbred Race Viewer (Racing API)")
st.markdown("This app fetches North American race meets and entries via The Racing API.")

date = st.date_input("Select Date", value=datetime.date.today())
date_str = date.strftime("%Y-%m-%d")
meets = fetch_meets(date_str)

valid_meets = [m for m in meets if m.get("track_name") and m.get("meet_id")]
if not valid_meets:
    st.warning("No valid meets found.")
    st.stop()

track_map = {f"{m['track_name']} ({m['country']})": m for m in valid_meets}
selected_label = st.selectbox("Select Track", list(track_map.keys()))
selected_meet = track_map[selected_label]

st.subheader(f"📍 {selected_meet['track_name']} - 🗓 {selected_meet['date']}")
st.caption(f"Meet ID: {selected_meet['meet_id']} | Country: {selected_meet['country']}")

races = fetch_entries(selected_meet["meet_id"])
if not races:
    st.info("No races available for this meet.")
else:
    for race in races:
        race_number = race.get("number", "Unknown")
        race_name = race.get("name", "Unnamed Race")
        st.markdown(f"### Race {race_number}: {race_name}")
        runners = race.get("runners", [])
        if runners:
            rows = []
            for r in runners:
                rows.append({
                    "Number": r.get("number"),
                    "Horse": r.get("horse"),
                    "Jockey": r.get("jockey", {}).get("alias", ""),
                    "Trainer": r.get("trainer", {}).get("alias", "")
                })
            st.dataframe(pd.DataFrame(rows))
        else:
            st.write("No runners.")
