
# 🏇 Real-Time Exotic Wager Overlay Dashboard

import streamlit as st
import pandas as pd
import datetime
import requests
import base64

# --- Title ---
st.set_page_config(page_title="Exotic Wager ROI Dashboard", layout="wide")
st.title("🎯 Exotic Wager Overlay Dashboard")
st.markdown("Color-coded ROI alerts for **exacta**, **trifecta**, and **superfecta** wagers at select tracks.")

# --- API Auth ---
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")
if not username or not password:
    st.error("Missing API credentials.")
    st.stop()

auth = base64.b64encode(f"{username}:{password}".encode()).decode()
headers = {"Authorization": f"Basic {auth}"}

# --- Config ---
TRACKS = {
    "Saratoga": "SAR",
    "Laurel Park": "LRL",
    "Churchill Downs": "CD"
}

def fetch_meets(date_str):
    url = f"https://api.theracingapi.com/v1/north-america/meets?date={date_str}"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return []
    return resp.json().get("meets", [])

def fetch_entries(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/entries"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return []
    return resp.json().get("races", [])

# --- Load Meets and Filter ---
today = datetime.date.today().strftime("%Y-%m-%d")
meets = fetch_meets(today)
meets = [m for m in meets if m.get("track_id") in TRACKS.values()]

if not meets:
    st.warning("No active meets at Saratoga, Laurel Park, or Churchill Downs.")
    st.stop()

# --- Display Wager Opportunities ---
for meet in meets:
    st.subheader(f"📍 {meet['track_name']} - {meet['date']}")
    races = fetch_entries(meet["meet_id"])
    for race in races:
        runners = race.get("runners", [])
        if len(runners) < 6:
            continue  # not enough for exotic wagering
        horses = [r.get("horse", {}).get("name", "N/A") for r in runners]
        st.markdown(f"**Race {race.get('number')}** - {race.get('name') or 'Unnamed'}")
        st.write("Horses:", ", ".join(horses))
        st.info("🔍 ROI Estimator Placeholder — Model logic goes here")
