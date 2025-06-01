import streamlit as st
import requests
from requests.auth import HTTPBasicAuth

st.title("🏇 Racing API - Raw Racecards Dump")
st.markdown("🔍 Fetching all available racecards without filters...")

API_USERNAME = st.secrets["RACING_API_USERNAME"]
API_PASSWORD = st.secrets["RACING_API_PASSWORD"]
auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)

url = "https://api.theracingapi.com/v1/racecards"
st.markdown(f"📡 Endpoint: `{url}`")

resp = requests.get(url, auth=auth)
if resp.status_code != 200:
    st.error(f"❌ Error fetching racecards: {resp.status_code} - {resp.text}")
    st.stop()

data = resp.json()
racecards = data.get("racecards", [])

if not racecards:
    st.warning("⚠️ No racecards found in response.")
else:
    st.success(f"✅ Retrieved {len(racecards)} racecards.")
    st.json(racecards[:5])
