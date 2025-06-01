import streamlit as st
import requests
from requests.auth import HTTPBasicAuth

st.title("🏇 UK Racecard Viewer - Test C: Alt Path")
API_USERNAME = st.secrets["RACING_API_USERNAME"]
API_PASSWORD = st.secrets["RACING_API_PASSWORD"]

auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
st.markdown("📅 Testing endpoint for date: **2025-05-31**")

url = "https://api.theracingapi.com/v1/gb/racecards/by-date/2025-05-31"
st.markdown(f"🔗 Endpoint: `https://api.theracingapi.com/v1/gb/racecards/by-date/2025-05-31`")

resp = requests.get(url, auth=auth)
if resp.status_code != 200:
    st.error(f"❌ Error: {resp.status_code} - {resp.text}")
    st.stop()

data = resp.json()
racecards = data.get("racecards", [])
uk_racecards = [r for r in racecards if r.get("region") == "GB"]

if not uk_racecards:
    st.warning("⚠️ No UK races found.")
else:
    st.success(f"✅ Found {len(uk_racecards)} races")
    for race in uk_racecards:
        st.subheader(race.get("race_name", "Unnamed Race"))
        st.write(f"**Course:** {race.get('course')}")
        st.write(f"**Off Time:** {race.get('off_time')}")
        st.write(f"**Distance:** {race.get('distance')}")
