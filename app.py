
# 🇺🇸 US Thoroughbred Race Viewer (Racing API) - Entries Only Debug

import streamlit as st
import requests
import base64
import datetime
import pandas as pd

# --- Load credentials ---
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")
if not username or not password:
    st.error("Missing API credentials in Streamlit secrets.")
    st.stop()

# --- Auth Header ---
auth_str = f"{username}:{password}"
auth_b64 = base64.b64encode(auth_str.encode()).decode()
headers = {"Authorization": f"Basic {auth_b64}"}

# --- API Calls ---
def fetch_meets(date_str):
    url = f"https://api.theracingapi.com/v1/north-america/meets?date={date_str}"
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        st.error(f"Failed to fetch meets: {res.status_code} - {res.text}")
        return []
    return res.json().get("meets", [])

def fetch_entries(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/entries"
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        st.error(f"Failed to fetch entries: {res.status_code} - {res.text}")
        return []
    return res.json().get("races", [])

# --- Streamlit UI ---
st.title("🇺🇸 US Thoroughbred Race Viewer (Racing API)")
st.markdown("This app fetches North American race meets and entries via The Racing API.")

date = st.date_input("Select Date", datetime.date.today())
date_str = date.strftime("%Y-%m-%d")
meets = fetch_meets(date_str)

if not meets:
    st.warning("No meets found.")
    st.stop()

track_map = {f"{m['track_name']} ({m['country']})": m for m in meets}
selected_track = st.selectbox("Select Track", list(track_map.keys()))
meet = track_map[selected_track]

st.markdown(f"📍 {meet['track_name']} - 🗓 {meet['date']}")
st.markdown(f"Meet ID: `{meet['meet_id']}` | Country: `{meet['country']}`")

races = fetch_entries(meet["meet_id"])
if not races:
    st.info("No race entries available.")
else:
    for race in races:
        st.subheader(f"Race {race.get('number', 'Unknown')}: {race.get('name', 'Unnamed Race')}")
        runners = race.get("runners", [])
        data = []
        for r in runners:
            data.append({
                "Number": r.get("number", "N/A"),
                "Horse": r.get("horse", "N/A"),
                "Jockey": r.get("jockey", {}).get("alias", "N/A") if isinstance(r.get("jockey"), dict) else "N/A",
                "Trainer": r.get("trainer", {}).get("alias", "N/A") if isinstance(r.get("trainer"), dict) else "N/A",
                "Odds": r.get("odds", {}).get("decimal", "N/A") if isinstance(r.get("odds"), dict) else "N/A"
            })
        df = pd.DataFrame(data)
        st.dataframe(df)
