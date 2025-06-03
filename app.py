
# 🇺🇸 US Thoroughbred Race Viewer (Racing API)
# Entries Only Version with Improved Field Handling

import streamlit as st
import requests
import base64
import datetime
import pandas as pd

# --- API Credentials ---
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")

if not username or not password:
    st.error("Missing API credentials in Streamlit secrets.")
    st.stop()

# --- Auth Header ---
basic_auth = f"{username}:{password}"
auth_header = base64.b64encode(basic_auth.encode()).decode()
headers = {
    "Authorization": f"Basic {auth_header}"
}

# --- Helper: Fetch Meets ---
def fetch_meets(date_str):
    url = f"https://api.theracingapi.com/v1/north-america/meets?date={date_str}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch meets: {response.status_code} - {response.text}")
        return []
    return response.json().get("meets", [])

# --- Helper: Fetch Entries ---
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

# --- Fetch Meets ---
meets = fetch_meets(date_str)
if not meets:
    st.warning("No meets found for selected date.")
    st.stop()

# --- Select Track ---
track_options = {f"{m['track_name']} ({m['country']})": m for m in meets}
selected_label = st.selectbox("Select Track", list(track_options.keys()))
selected_meet = track_options[selected_label]

st.markdown(f"📍 **{selected_meet['track_name']}** - 🗓 {selected_meet['date']}")
st.markdown(f"Meet ID: `{selected_meet['meet_id']}` | Country: `{selected_meet['country']}`")

# --- Fetch and Display Entries ---
races = fetch_entries(selected_meet['meet_id'])
for race in races:
    race_number = race.get("number", "Unknown")
    race_name = race.get("name", "Unnamed Race")
    st.subheader(f"Race {race_number}: {race_name}")

    runners = race.get("runners", [])
    if runners:
        df = pd.DataFrame()
        for runner in runners:
            df = pd.concat([
                df,
                pd.DataFrame([{
                    "Number": runner.get("number", ""),
                    "Horse": runner.get("horse", ""),
                    "Jockey": runner.get("jockey", {}).get("alias", ""),
                    "Trainer": runner.get("trainer", {}).get("alias", "")
                }])
            ])
        st.dataframe(df)
    else:
        st.write("No runners available.")
