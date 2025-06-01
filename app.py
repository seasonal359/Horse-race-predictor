import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

API_USERNAME = st.secrets["RACING_API_USERNAME"]
API_PASSWORD = st.secrets["RACING_API_PASSWORD"]

st.title("🏇 UK Racecard Viewer (Racing API)")
st.markdown("🔍 Fetching UK racecards for **yesterday**...")

auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
yesterday = "2025-05-31"
url = f"https://api.theracingapi.com/v1/racecards/by-date/" + yesterday

resp = requests.get(url, auth=auth)
if resp.status_code != 200:
    st.error(f"❌ Error fetching racecards: {resp.status_code} - {resp.text}")
    st.stop()

data = resp.json()
racecards = data.get("racecards", [])
uk_racecards = [r for r in racecards if r.get("region") == "GB"]

if not uk_racecards:
    st.warning("❌ No UK races found for yesterday.")
else:
    st.success(f"✅ Found {len(uk_racecards)} UK races on {yesterday}")
    for race in uk_racecards:
        st.subheader(race.get("race_name", "Unnamed Race"))
        st.write(f"**Course:** {race.get('course')}")
        st.write(f"**Off Time:** {race.get('off_time')}")
        st.write(f"**Distance:** {race.get('distance')}")
        st.write("---")
