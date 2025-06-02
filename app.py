
# 🇺🇸 US Thoroughbred Race Viewer (Racing API) - Resilient Field Handling

import streamlit as st
import requests
import base64
import datetime
import pandas as pd

username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")
if not username or not password:
    st.error("Missing API credentials in Streamlit secrets.")
    st.stop()

auth_header = base64.b64encode(f"{username}:{password}".encode()).decode()
headers = { "Authorization": f"Basic {auth_header}" }

def fetch_meets(date_str):
    url = f"https://api.theracingapi.com/v1/north-america/meets?date={date_str}"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error(f"Failed to fetch meets: {r.status_code} - {r.text}")
        return []
    return r.json().get("meets", [])

def fetch_entries(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/entries"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error(f"Failed to fetch entries: {r.status_code} - {r.text}")
        return []
    return r.json().get("races", [])

def fetch_results(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/results"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error(f"Failed to fetch results: {r.status_code} - {r.text}")
        return []
    return r.json().get("races", [])

st.title("🇺🇸 US Thoroughbred Race Viewer (Racing API)")
st.markdown("This app fetches North American race meets, entries, and results via The Racing API.")

date = st.date_input("Select Date", value=datetime.date.today())
date_str = date.strftime("%Y-%m-%d")

st.markdown("🔍 Fetching race data from The Racing API...")
meets = fetch_meets(date_str)

valid_meets = [m for m in meets if m.get("track_name") and m.get("meet_id")]
if not valid_meets:
    st.warning("No valid race meets found for the selected date.")
    st.json(meets)
    st.stop()

track_options = {f"{m['track_name']} ({m['country']})": m for m in valid_meets}
selected_label = st.selectbox("Select Track", list(track_options.keys()))
selected_meet = track_options[selected_label]

st.subheader(f"📍 {selected_meet['track_name']} - 🗓 {selected_meet['date']}")
st.write(f"Meet ID: `{selected_meet['meet_id']}` | Country: `{selected_meet['country']}`")

if st.checkbox("Show Race Entries"):
    entries = fetch_entries(selected_meet['meet_id'])
    if entries:
        for race in entries:
            st.markdown(f"### Race {race.get('number')}: {race.get('name')}")
            runners = race.get("runners", [])
            if runners:
                df = pd.DataFrame(runners)
                cols = [col for col in ['number', 'horse', 'jockey', 'trainer'] if col in df.columns]
                if cols:
                    st.dataframe(df[cols])
                else:
                    st.warning("Expected runner columns not found.")
                    st.dataframe(df)
            else:
                st.warning("No runners for this race.")
    else:
        st.info("No race entries returned.")

if st.checkbox("Show Race Results"):
    results = fetch_results(selected_meet['meet_id'])
    if results:
        for race in results:
            st.markdown(f"### Race {race.get('number')}: {race.get('name')}")
            out = race.get("results", [])
            if out:
                df = pd.DataFrame(out)
                cols = [col for col in ['number', 'horse', 'position', 'jockey', 'trainer'] if col in df.columns]
                if cols:
                    st.dataframe(df[cols])
                else:
                    st.warning("Expected result columns not found.")
                    st.dataframe(df)
            else:
                st.warning("No results for this race.")
    else:
        st.info("No race results returned.")
