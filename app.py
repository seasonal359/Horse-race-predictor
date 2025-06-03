
# 🇺🇸 US Thoroughbred Race Viewer (Racing API) - Updated to Correctly Display Runners and Odds

import streamlit as st
import requests
import base64
import datetime
import pandas as pd

# --- Auth Setup ---
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")
if not username or not password:
    st.error("Missing API credentials in Streamlit secrets.")
    st.stop()

auth_str = f"{username}:{password}"
auth_header = base64.b64encode(auth_str.encode()).decode()
headers = {
    "Authorization": f"Basic {auth_header}"
}

# --- API Calls ---
def fetch_meets(date_str):
    url = f"https://api.theracingapi.com/v1/north-america/meets?date={date_str}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch meets: {response.status_code} - {response.text}")
        return []
    return response.json().get("meets", [])

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
    st.warning("No race meets found for the selected date.")
    st.stop()

track_options = {f"{m['track_name']} ({m['country']})": m for m in meets}
track_name = st.selectbox("Select Track", list(track_options.keys()))
selected_meet = track_options[track_name]

st.subheader(f"📍 {selected_meet['track_name']} - 🗓 {selected_meet['date']}")
st.write(f"Meet ID: `{selected_meet['meet_id']}` | Country: `{selected_meet['country']}`")

races = fetch_entries(selected_meet["meet_id"])

for race in races:
    race_number = race.get("number", "Unknown")
    race_name = race.get("name", "Unnamed Race")
    st.markdown(f"### Race {race_number}: {race_name}")

    runners = race.get("runners", [])
    data = []
    for r in runners:
        number = r.get("number", "N/A")
        horse_name = r.get("horse", {}).get("name", "N/A")
        jockey = r.get("jockey", {}).get("alias", "N/A")
        trainer = r.get("trainer", {}).get("alias", "N/A")
        odds = r.get("odds", {}).get("decimal", "N/A")
        data.append({
            "Number": number,
            "Horse": horse_name,
            "Jockey": jockey,
            "Trainer": trainer,
            "Odds": odds
        })

    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)
    else:
        st.info("No runners found for this race.")
