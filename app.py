
# 🇺🇸 US Thoroughbred Race Viewer (Racing API) - Entries Only with Clean Output

import streamlit as st
import requests
import base64
import datetime
import pandas as pd

# --- Auth from Streamlit secrets ---
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")
if not username or not password:
    st.error("Missing API credentials in Streamlit secrets.")
    st.stop()

auth_string = f"{username}:{password}"
auth_header = base64.b64encode(auth_string.encode()).decode()
headers = {
    "Authorization": f"Basic {auth_header}"
}

# --- Fetch Meets ---
def fetch_meets(date_str):
    url = f"https://api.theracingapi.com/v1/north-america/meets?date={date_str}"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error(f"Failed to fetch meets: {r.status_code} - {r.text}")
        return []
    return r.json().get("meets", [])

# --- Fetch Entries ---
def fetch_entries(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/entries"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error(f"Failed to fetch entries: {r.status_code} - {r.text}")
        return []
    return r.json().get("races", [])

# --- Streamlit UI ---
st.title("🇺🇸 US Thoroughbred Race Viewer (Racing API)")
st.markdown("This app fetches North American race meets and entries via The Racing API.")

date = st.date_input("Select Date", value=datetime.date.today())
date_str = date.strftime("%Y-%m-%d")

meets = fetch_meets(date_str)
valid_meets = [m for m in meets if m.get("track_name") and m.get("meet_id")]
if not valid_meets:
    st.warning("No meets with valid locations and IDs were returned.")
    st.stop()

track_map = {f"{m['track_name']} ({m['country']})": m for m in valid_meets}
track_choice = st.selectbox("Select Track", list(track_map.keys()))
selected_meet = track_map[track_choice]

st.subheader(f"📍 {selected_meet['track_name']} - 🗓 {selected_meet['date']}")
st.write(f"Meet ID: {selected_meet['meet_id']} | Country: {selected_meet['country']}")

races = fetch_entries(selected_meet['meet_id'])

for race in races:
    race_number = race.get("number", "Unknown")
    race_name = race.get("name", "Unnamed Race")
    st.markdown(f"### Race {race_number}: {race_name}")

    runners = race.get("runners", [])
    if runners:
        flat_runners = []
        for r in runners:
            flat_runners.append({
                "Number": r.get("number"),
                "Horse": r.get("horse"),
                "Jockey": r.get("jockey", {}).get("last_name", ""),
                "Trainer": r.get("trainer", {}).get("last_name", ""),
                "Post Pos": r.get("post_position"),
                "Weight": r.get("weight"),
                "Odds": r.get("morning_line")
            })
        st.dataframe(pd.DataFrame(flat_runners))
    else:
        st.info("No runners found for this race.")
