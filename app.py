import streamlit as st
import requests
from requests.auth import _basic_auth_str

# Load credentials from Streamlit Cloud secrets
API_USERNAME = st.secrets["RACING_API_USERNAME"]
API_PASSWORD = st.secrets["RACING_API_PASSWORD"]

st.title("🏇 US Thoroughbred Race Viewer (Racing API)")
st.markdown("🔍 Fetching race data from The Racing API...")

# Manual header construction to match curl behavior
auth_header = _basic_auth_str(API_USERNAME, API_PASSWORD)
st.text(f"📡 Sending header: {auth_header[:30]}...")

headers = {
    "Authorization": auth_header
}

api_url = "https://api.theracingapi.com/v1/racecards"

response = requests.get(api_url, headers=headers)

if response.status_code == 200:
    data = response.json()
    if not data:
        st.warning("No race data available.")
    else:
        st.success("Races loaded successfully.")
        for race in data[:10]:
            st.subheader(race.get("track_name", "Unknown Track"))
            st.write(race)
else:
    st.error(f"Failed to fetch data: {response.status_code} - {response.text}")
