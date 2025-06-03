# 🇺🇸 US Thoroughbred Race Viewer (Racing API)
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

# --- Prepare headers ---
auth_string = f"{username}:{password}"
auth_header = base64.b64encode(auth_string.encode()).decode()
headers = {
    "Authorization": f"Basic {auth_header}"
}

# --- API Requests ---
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
        st.warning(f"Entries fetch failed: {response.status_code}")
        return []
    return response.json().get("races", [])

def fetch_results(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/results"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.warning(f"Results fetch failed: {response.status_code}")
        return []
    return response.json().get("races", [])

# --- UI ---
st.title("🇺🇸 US Thoroughbred Race Viewer (Racing API)")
date = st.date_input("Pick a date", datetime.date.today())
date_str = date.strftime("%Y-%m-%d")

meets = fetch_meets(date_str)
if not meets:
    st.warning("No meets found for this date.")
    st.stop()

track_map = {f"{m['track_name']} ({m['country']})": m for m in meets}
selected_label = st.selectbox("Select Track", list(track_map))
meet = track_map[selected_label]

st.subheader(f"📍 {meet['track_name']} - 🗓 {meet['date']}")
st.write(f"Meet ID: `{meet['meet_id']}` | Country: `{meet['country']}`")

# --- Entries ---
if st.checkbox("Show Entries"):
    entries = fetch_entries(meet["meet_id"])
    for race in entries:
        st.markdown(f"### Race {race.get('number')}: {race.get('name')}")
        if 'runners' in race:
            df = pd.DataFrame(race['runners'])
            fields = [f for f in ['number', 'horse', 'jockey', 'trainer', 'morning_line'] if f in df.columns]
            st.dataframe(df[fields])
        else:
            st.info("No runners listed.")

# --- Results ---
if st.checkbox("Show Results"):
    results = fetch_results(meet["meet_id"])
    for race in results:
        st.markdown(f"### Result - Race {race.get('number')}: {race.get('name')}")
        if 'results' in race:
            df = pd.DataFrame(race['results'])
            fields = [f for f in ['position', 'horse', 'jockey', 'trainer', 'odds'] if f in df.columns]
            st.dataframe(df[fields])
        else:
            st.info("No results found.")
