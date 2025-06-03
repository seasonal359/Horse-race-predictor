
# 🇺🇸 US Thoroughbred Race Viewer (Racing API)
import streamlit as st
import requests
import base64
import datetime
import pandas as pd

# Load API credentials
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")
if not username or not password:
    st.error("Missing API credentials.")
    st.stop()

auth = base64.b64encode(f"{username}:{password}".encode()).decode()
headers = { "Authorization": f"Basic {auth}" }

# Helper functions
def fetch_meets(date_str):
    url = f"https://api.theracingapi.com/v1/north-america/meets?date={date_str}"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error(f"Error fetching meets: {r.status_code}")
        return []
    return r.json().get("meets", [])

def fetch_entries(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/entries"
    r = requests.get(url, headers=headers)
    return r.json().get("races", []) if r.status_code == 200 else []

def fetch_results(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/results"
    r = requests.get(url, headers=headers)
    return r.json().get("races", []) if r.status_code == 200 else []

# UI
st.title("🇺🇸 US Thoroughbred Race Viewer (Racing API)")
date = st.date_input("Select Date", value=datetime.date.today())
date_str = date.strftime("%Y-%m-%d")

meets = fetch_meets(date_str)
valid_meets = [m for m in meets if m.get("track_name") and m.get("meet_id")]
if not valid_meets:
    st.warning("No valid meets returned.")
    st.json(meets)
    st.stop()

track_options = [f"{m['track_name']} ({m['country']})" for m in valid_meets]
selected = st.selectbox("Select Track", track_options)
meet = valid_meets[track_options.index(selected)]

st.subheader(f"{meet['track_name']} - {meet['date']}")
st.write(f"Meet ID: {meet['meet_id']}")

if st.checkbox("Show Entries"):
    entries = fetch_entries(meet["meet_id"])
    for race in entries:
        st.markdown(f"### Race {race.get('number')}: {race.get('name')}")
        df = pd.DataFrame(race.get("runners", []))
        if not df.empty:
            keep = [c for c in ["number", "horse", "jockey", "trainer"] if c in df.columns]
            st.dataframe(df[keep])

if st.checkbox("Show Results"):
    results = fetch_results(meet["meet_id"])
    for race in results:
        st.markdown(f"### Race {race.get('number')}: {race.get('name')}")
        df = pd.DataFrame(race.get("results", []))
        if not df.empty:
            keep = [c for c in ["number", "horse", "position", "jockey", "trainer"] if c in df.columns]
            st.dataframe(df[keep])
