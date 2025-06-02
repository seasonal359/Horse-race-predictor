
import streamlit as st
import requests
import base64
from datetime import datetime

st.set_page_config(page_title="US Thoroughbred Race Viewer (Racing API)", layout="centered")

st.title("🇺🇸 US Thoroughbred Race Viewer (Racing API)")
st.write("🔍 Fetching race data from The Racing API...")

# Read secrets from Streamlit's secrets
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")

if not username or not password:
    st.error("Missing API credentials in Streamlit secrets.")
    st.stop()

# Build Basic Auth Header
credentials = f"{username}:{password}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()
headers = {
    "Authorization": f"Basic {encoded_credentials}"
}

# Get today's date
today = datetime.today().strftime("%Y-%m-%d")
url = f"https://api.theracingapi.com/v1/north-america/meets?date={today}"

st.text(f"📡 Sending header: Basic {encoded_credentials[:30]}...")

response = requests.get(url, headers=headers)
if response.status_code != 200:
    st.error(f"Failed to fetch data: {response.status_code} - {response.text}")
    st.stop()

data = response.json()
if not data.get("meets"):
    st.warning("No U.S. races found in API response.")
    st.json(data)
else:
    st.success(f"✅ Found {len(data['meets'])} meets today.")
    for meet in data["meets"]:
        st.markdown(f"### {meet.get('track')}")
        st.write(f"🗓 Date: {meet.get('date')}")
        st.write(f"📍 Location: {meet.get('location')}")
