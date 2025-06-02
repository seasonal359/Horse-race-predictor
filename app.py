
import streamlit as st
import requests
import base64
import datetime
import json

st.title("🔧 Racing API Debug - Meets Only")

# Load credentials
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")

if not username or not password:
    st.error("Missing credentials in Streamlit secrets.")
    st.stop()

# Encode auth
basic_auth = f"{username}:{password}"
auth_header = base64.b64encode(basic_auth.encode()).decode()
headers = { "Authorization": f"Basic {auth_header}" }

st.markdown("📡 Sending request to /meets...")

# Use fixed date for debug
date_str = datetime.date.today().strftime("%Y-%m-%d")
url = f"https://api.theracingapi.com/v1/north-america/meets?date={date_str}"

st.code(f"GET {url}")
st.code(f"Headers: {headers}")

# Make the request
try:
    response = requests.get(url, headers=headers, timeout=10)
    st.code(f"Status: {response.status_code}")
    if response.status_code == 200:
        st.json(response.json())
    else:
        st.error(f"Failed: {response.status_code}")
        st.text(response.text)
except Exception as e:
    st.error(f"Exception: {e}")
