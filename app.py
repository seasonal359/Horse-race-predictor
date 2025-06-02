# 🇺🇸 US Thoroughbred Race Viewer (Racing API) - Full Debug & Error Handling

import streamlit as st
import requests
import base64
import datetime
import pandas as pd

# --- Helper: Build Auth Header from Streamlit Secrets ---
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")
if not username or not password:
    st.error("Missing API credentials in Streamlit secrets.")
    st.stop()

basic_auth = f"{username}:{password}"
auth_header = base64.b64encode(basic_auth.encode()).decode()
headers = {
    "Authorization": f"Basic {auth_header}"
}

# --- Get Meets ---
def fetch_meets(date_str):
    url = f"https://api.theracingapi.com/v1/north-america/meets?date={date_str}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch meets: {response.status_code} - {response.text}")
        return [], response.text
    return response.json().get("meets", []), response.text

# --- Get Entries for a Meet ---
def fetch_entries(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/entries"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch entries: {response.status_code} - {response.text}")
        return []
    return response.json().get("races", [])

# --- Get Results for a Meet ---
def fetch_results(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/results"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch results: {response.status_code} - {response.text}")
        return []
    return response.json().get("races", [])

# --- Streamlit App ---
st.title("🇺🇸 US Thoroughbred Race Viewer (Racing API)")
st.markdown("This app fetches North American race meets, entries, and results via The Racing API.")

# --- Select Date ---
date = st.date_input("Select Date", value=datetime.date.today())
date_str = date.strftime("%Y-%m-%d")

# --- Fetch and Select Track ---
st.markdown("🔍 Fetching race data from The Racing API...")
meets, raw_response = fetch_meets(date_str)

if not meets:
    st.warning("No valid race meets found for the selected date.")
    st.code(raw_response, language='json')
    st.stop()

track_options = {
    f"{meet.get('location', 'Unknown')} ({meet.get('country', 'N/A')})": meet
    for meet in meets if 'location' in meet and 'id' in meet
}

if not track_options:
    st.warning("No meets with valid locations and IDs were returned.")
    st.code(raw_response, language='json')
    st.stop()

selected_track_label = st.selectbox("Select Track", list(track_options.keys()))
selected_meet = track_options.get(selected_track_label)

# --- Display Basic Meet Info ---
if selected_meet:
    st.subheader(f"📍 {selected_meet.get('location')} - 🗓 {selected_meet.get('date')}")
    st.write(f"Meet ID: `{selected_meet.get('id')}` | Country: `{selected_meet.get('country')}`")

    # --- Fetch and Show Entries ---
    if st.checkbox("Show Race Entries"):
        races = fetch_entries(selected_meet['id'])
        if races:
            for race in races:
                st.markdown(f"### Race {race.get('number')}: {race.get('name')}")
                if 'runners' in race:
                    df = pd.DataFrame(race['runners'])
                    st.dataframe(df[['number', 'horse', 'jockey', 'trainer']])
                else:
                    st.warning("No runners found for this race.")
        else:
            st.info("No race entries available.")

    # --- Fetch and Show Results ---
    if st.checkbox("Show Race Results"):
        results = fetch_results(selected_meet['id'])
        if results:
            for race in results:
                st.markdown(f"### Race {race.get('number')}: {race.get('name')}")
                if 'results' in race:
                    df = pd.DataFrame(race['results'])
                    st.dataframe(df[['number', 'horse', 'position', 'jockey', 'trainer']])
                else:
                    st.warning("No results found for this race.")
        else:
            st.info("No race results available.")
else:
    st.warning("No valid meet selected.")
    st.code(raw_response, language='json')
