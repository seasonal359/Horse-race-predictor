import streamlit as st
import requests
import os
from requests.auth import _basic_auth_str
from dotenv import load_dotenv

load_dotenv()
API_USERNAME = os.getenv("RACING_API_USERNAME")
API_PASSWORD = os.getenv("RACING_API_PASSWORD")

st.title("🏇 US Thoroughbred Race Viewer (Racing API)")
st.markdown("🔍 Fetching race data from The Racing API...")

# Debug: Show a preview of the username and header
if API_USERNAME and API_PASSWORD:
    auth_header = _basic_auth_str(API_USERNAME, API_PASSWORD)
    st.text(f"📡 Sending header: {auth_header[:30]}...")
else:
    st.error("Missing API credentials.")

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
