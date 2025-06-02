
import streamlit as st
import requests
from datetime import datetime
import base64

st.set_page_config(page_title="🇬🇧 UK Racecard Viewer (Racing API)", layout="centered")
st.title("🇬🇧 UK Racecard Viewer (Racing API)")

# Load credentials from Streamlit secrets
username = st.secrets.get("racingapi_username")
password = st.secrets.get("racingapi_password")

if not username or not password:
    st.error("Missing API credentials.")
    st.stop()

# Encode credentials
credentials = f"{username}:{password}"
auth_header = "Basic " + base64.b64encode(credentials.encode()).decode()

headers = {
    "Authorization": auth_header
}

# Fetch today's UK races
today = datetime.today().strftime("%Y-%m-%d")
st.write(f"📅 Fetching UK race data from The Racing API for {today}...")

url = f"https://api.theracingapi.com/regions/gb/racecards?date={today}"

response = requests.get(url, headers=headers)
if response.status_code != 200:
    st.error(f"Failed to fetch data: {response.status_code} - {response.text}")
    st.stop()

data = response.json()
races = data.get("racecards", [])

if not races:
    st.warning("❌ No UK races found in API response.")
else:
    for race in races:
        st.markdown(f"**Course:** {race.get('course')}")
        st.markdown(f"**Race Name:** {race.get('race_name')}")
        st.markdown(f"**Time:** {race.get('off_time')}")
        st.markdown("---")
