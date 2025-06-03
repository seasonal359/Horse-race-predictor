
import streamlit as st
import requests
import base64
import datetime
import pandas as pd

# --- Auth from Streamlit Secrets ---
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")
if not username or not password:
    st.error("Missing API credentials in Streamlit secrets.")
    st.stop()

auth = base64.b64encode(f"{username}:{password}".encode()).decode()
headers = {"Authorization": f"Basic {auth}"}

# --- Fetch Meets ---
def fetch_meets(date_str):
    url = f"https://api.theracingapi.com/v1/north-america/meets?date={date_str}"
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        st.error(f"Failed to fetch meets: {res.status_code} - {res.text}")
        return []
    return res.json().get("meets", [])

# --- Fetch Entries ---
def fetch_entries(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/entries"
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        st.error(f"Failed to fetch entries: {res.status_code} - {res.text}")
        return []
    return res.json().get("races", [])

# --- App UI ---
st.title("🇺🇸 US Thoroughbred Race Viewer (Racing API)")
st.markdown("This app fetches North American race meets and entries via The Racing API.")

date = st.date_input("Select Date", value=datetime.date.today())
date_str = date.strftime("%Y-%m-%d")

st.markdown("🔍 Fetching race data from The Racing API...")
meets = fetch_meets(date_str)
if not meets:
    st.warning("No meets returned.")
    st.stop()

# Build dropdown options
track_dict = {f"{m['track_name']} ({m['country']})": m for m in meets if 'track_name' in m}
selected_label = st.selectbox("Select Track", list(track_dict.keys()))
selected_meet = track_dict[selected_label]
meet_id = selected_meet['meet_id']

st.subheader(f"📍 {selected_meet['track_name']} - 🗓 {selected_meet['date']}")
st.write(f"Meet ID: `{meet_id}` | Country: `{selected_meet['country']}`")

# Fetch and display entries
races = fetch_entries(meet_id)
if not races:
    st.info("No races returned.")
    st.stop()

for race in races:
    race_number = race.get("number", "Unknown")
    race_name = race.get("name", "Unnamed Race")
    st.markdown(f"### Race {race_number}: {race_name}")

    runners = race.get("runners", [])
    data = []
    for r in runners:
        horse_name = r.get("horse", "N/A")
        jockey = r.get("jockey", {}).get("alias", "N/A")
        trainer = r.get("trainer", {}).get("alias", "N/A")
        number = r.get("number", "N/A")
        odds = r.get("odds", {}).get("decimal", "N/A")
        data.append({
            "Number": number,
            "Horse": horse_name,
            "Jockey": jockey,
            "Trainer": trainer,
            "Odds": odds
        })
    df = pd.DataFrame(data)
    st.dataframe(df)
