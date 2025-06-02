
# 🇺🇸 US Thoroughbred Race Viewer (Racing API) - Safe Entries + Results

import streamlit as st
import requests
import base64
import datetime
import pandas as pd

# --- Title and App Ready Message ---
st.title("🇺🇸 US Thoroughbred Race Viewer (Racing API)")
st.markdown("This app fetches North American race meets, entries, and results via The Racing API.")
st.success("✅ App Loaded")

# --- Build Auth Header from Streamlit Secrets ---
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")
if not username or not password:
    st.error("Missing API credentials in Streamlit secrets.")
    st.stop()

auth = f"{username}:{password}"
auth_header = base64.b64encode(auth.encode()).decode()
headers = {
    "Authorization": f"Basic {auth_header}"
}

# --- Get Meets ---
def fetch_meets(date_str):
    url = f"https://api.theracingapi.com/v1/north-america/meets?date={date_str}"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error(f"Failed to fetch meets: {r.status_code} - {r.text}")
        return []
    return r.json().get("meets", [])

# --- Get Entries ---
def fetch_entries(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/entries"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error(f"Failed to fetch entries: {r.status_code} - {r.text}")
        return []
    return r.json().get("races", [])

# --- Get Results ---
def fetch_results(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/results"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.warning(f"Results not available: {r.status_code} - {r.text}")
        return []
    return r.json().get("races", [])

# --- UI: Select Date ---
date = st.date_input("Select Date", value=datetime.date.today())
date_str = date.strftime("%Y-%m-%d")
today = datetime.date.today()

# --- Fetch Meets ---
st.markdown("🔍 Fetching race data from The Racing API...")
meets = fetch_meets(date_str)

valid_meets = [m for m in meets if m.get("meet_id") and m.get("track_name")]
if not valid_meets:
    st.warning("No valid race meets found for the selected date.")
    st.json(meets)
    st.stop()

# --- Track Selection ---
track_labels = {f"{m['track_name']} ({m['country']})": m for m in valid_meets}
track_choice = st.selectbox("Select Track", list(track_labels.keys()))
selected_meet = track_labels[track_choice]
meet_id = selected_meet.get("meet_id")

st.subheader(f"📍 {selected_meet['track_name']} - 🗓 {selected_meet['date']}")
st.write(f"Meet ID: {meet_id}")

# --- Show Entries ---
if st.checkbox("Show Entries"):
    st.markdown("📋 Fetching entries...")
    races = fetch_entries(meet_id)
    if not races:
        st.info("No entries found.")
    else:
        for race in races:
            st.markdown(f"### Race {race.get('number')}: {race.get('name', 'No Name')}")
            if "runners" in race:
                runners = race["runners"]
                df = pd.DataFrame(runners)
                cols = [col for col in ["number", "horse", "jockey", "trainer"] if col in df.columns]
                if cols:
                    st.dataframe(df[cols])
                else:
                    st.write("No recognizable runner columns.")
            else:
                st.write("No runners available.")

# --- Show Results ---
if st.checkbox("Show Results"):
    if date > today:
        st.info("Results not available for future dates.")
    else:
        st.markdown("📊 Fetching results...")
        races = fetch_results(meet_id)
        if not races:
            st.info("No results returned.")
        else:
            for race in races:
                st.markdown(f"### Race {race.get('number')}: {race.get('name', 'No Name')}")
                if "results" in race:
                    results = race["results"]
                    df = pd.DataFrame(results)
                    cols = [col for col in ["number", "horse", "position", "jockey", "trainer"] if col in df.columns]
                    if cols:
                        st.dataframe(df[cols])
                    else:
                        st.write("No recognizable result columns.")
                else:
                    st.write("No results available.")
