
# ✅ Safe Streamlit Template for US Thoroughbred Race Viewer
import streamlit as st
import requests
import base64
import datetime
import pandas as pd

st.set_page_config(page_title="🇺🇸 US Race Viewer", layout="centered")
st.title("🇺🇸 US Thoroughbred Race Viewer (Racing API)")
st.markdown("This app fetches North American race meets, entries, and results via The Racing API.")

# 🛑 DEBUG: Confirm app is rendering
st.info("✅ App Loaded")

# 🔐 Check secrets
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")
if not username or not password:
    st.error("Missing API credentials in Streamlit secrets.")
    st.stop()

# 🔐 Auth Header
try:
    auth_header = base64.b64encode(f"{username}:{password}".encode()).decode()
except Exception as e:
    st.error(f"Encoding Error: {e}")
    st.stop()

headers = {
    "Authorization": f"Basic {auth_header}"
}

# 📅 Date selector
date = st.date_input("Select Date", value=datetime.date.today())
date_str = date.strftime("%Y-%m-%d")

# 🧲 Fetch Meets
st.markdown("🔍 Fetching race data from The Racing API...")
try:
    url = f"https://api.theracingapi.com/v1/north-america/meets?date={date_str}"
    response = requests.get(url, headers=headers)
    data = response.json()
except Exception as e:
    st.error(f"❌ API request failed: {e}")
    st.stop()

if response.status_code != 200:
    st.error(f"❌ Failed to fetch meets: {response.status_code} - {response.text}")
    st.stop()

meets = data.get("meets", [])
if not meets:
    st.warning("⚠️ No meets found.")
    st.json(data)
    st.stop()

# 🧾 Display available tracks
track_names = [f"{m.get('track_name')} ({m.get('country')})" for m in meets]
track_ids = [m.get("meet_id") for m in meets]

selected = st.selectbox("Select Track", track_names)
index = track_names.index(selected)
selected_meet = meets[index]

st.subheader(f"📍 {selected_meet.get('track_name')} - 🗓 {selected_meet.get('date')}")
st.code(f"Meet ID: {selected_meet.get('meet_id')}")

st.success("🎯 If you see this message, Streamlit rendering works. Next step is enabling entries and results.")
