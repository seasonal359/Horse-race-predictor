import streamlit as st
import requests
import os
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()
API_USERNAME = os.getenv("RACING_API_USERNAME")
API_PASSWORD = os.getenv("RACING_API_PASSWORD")

st.title("🏇 US Thoroughbred Race Viewer (Racing API)")

api_url = "https://api.theracingapi.com/v1/racecards"

# Fetch race data
st.markdown("🔍 Fetching race data from The Racing API...")

response = requests.get(api_url, auth=HTTPBasicAuth(API_USERNAME, API_PASSWORD))

if response.status_code == 200:
    data = response.json()
    if not data:
        st.warning("No race data available.")
    else:
        st.success("Races loaded successfully.")
        for race in data[:10]:  # Show a few races
            st.subheader(race.get("track_name", "Unknown Track"))
            st.write(race)
else:
    st.error(f"Failed to fetch data: {response.status_code} - {response.text}")
