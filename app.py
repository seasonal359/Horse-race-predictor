import streamlit as st
import requests
from requests.auth import _basic_auth_str

# Load credentials from Streamlit Cloud secrets
API_USERNAME = st.secrets["RACING_API_USERNAME"]
API_PASSWORD = st.secrets["RACING_API_PASSWORD"]

st.title("🏇 UK Race Viewer (Racing API)")
st.markdown("🔍 Fetching UK race data from The Racing API...")

auth_header = _basic_auth_str(API_USERNAME, API_PASSWORD)
st.text(f"📡 Sending header: {auth_header[:30]}...")

headers = {
    "Authorization": auth_header
}

api_url = "https://api.theracingapi.com/v1/uk/racecards"

response = requests.get(api_url, headers=headers)

if response.status_code == 200:
    data = response.json()
    racecards = data.get("racecards", [])

    if not racecards:
        st.warning("No UK races found in API response.")
        st.subheader("🔎 Raw API Response:")
        st.json(data)
    else:
        st.success(f"{len(racecards)} UK races loaded.")
        for race in racecards[:10]:
            st.subheader(f"{race.get('course', 'Unknown Track')} - {race.get('race_name', '')}")
            st.write(race)
else:
    st.error(f"Failed to fetch data: {response.status_code} - {response.text}")
