
# 🇺🇸 US Thoroughbred Race Viewer (Racing API)
import streamlit as st
import requests
import base64
import datetime
import pandas as pd

# --- Auth ---
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")
if not username or not password:
    st.error("Missing API credentials.")
    st.stop()

auth = base64.b64encode(f"{username}:{password}".encode()).decode()
headers = { "Authorization": f"Basic {auth}" }

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

# --- UI ---
st.title("🇺🇸 US Thoroughbred Race Viewer (Racing API)")
st.markdown("This app fetches North American race meets and entries via The Racing API.")

date = st.date_input("Select Date", value=datetime.date.today())
date_str = date.strftime("%Y-%m-%d")

meets = fetch_meets(date_str)
if not meets:
    st.warning("No meets returned.")
    st.stop()

track_map = {f"{m['track_name']} ({m['country']})": m for m in meets if 'track_name' in m and 'meet_id' in m}
track_choice = st.selectbox("Select Track", list(track_map.keys()))
meet = track_map[track_choice]

st.subheader(f"📍 {meet['track_name']} - 🗓 {meet['date']}")
st.write(f"Meet ID: `{meet['meet_id']}` | Country: `{meet['country']}`")

# --- Entries ---
races = fetch_entries(meet['meet_id'])
for i, race in enumerate(races):
    race_num = race.get("number") or f"{i+1}"
    race_name = race.get("name") or "Unnamed Race"
    st.markdown(f"### Race {race_num}: {race_name}")

    runners = race.get("runners")
    if runners:
        df = pd.json_normalize(runners)
        cols_to_show = []
        for col in df.columns:
            if any(x in col for x in ["number", "horse", "jockey", "trainer"]):
                cols_to_show.append(col)
        if cols_to_show:
            st.dataframe(df[cols_to_show])
        else:
            st.warning("No expected runner fields found.")
    else:
        st.info("No runners listed.")
