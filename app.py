
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.title("🇬🇧 UK Racecard Viewer (Racing API)")
st.write("🔍 Fetching UK race data from The Racing API...")

# ✅ Correct way to access Streamlit secrets
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")

if not username or not password:
    st.error("❌ Missing API credentials. Set them in Streamlit secrets.")
    st.stop()

import base64
auth_str = f"{username}:{password}"
auth_header = "Basic " + base64.b64encode(auth_str.encode()).decode()

headers = {
    "Authorization": auth_header
}

today = datetime.today().strftime("%Y-%m-%d")
url = f"https://api.theracingapi.com/racecards?region=gb&date={today}"
st.write(f"📡 Sending header: {auth_header[:40]}...")

response = requests.get(url, headers=headers)
if response.status_code != 200:
    st.error(f"Failed to fetch data: {response.status_code} - {response.text}")
    st.stop()

data = response.json()
racecards = data.get("racecards", [])

if not racecards:
    st.warning("No UK races found in API response.")
else:
    st.success(f"✅ Found {len(racecards)} races.")
    for race in racecards[:5]:
        st.subheader(f"{race['course']} - {race['race_name']}")
        st.write(f"Off Time: {race['off_time']} | Distance: {race['distance']}")
