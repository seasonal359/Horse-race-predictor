
import streamlit as st
import requests
import base64
from datetime import datetime

st.title("🇬🇧 UK Racecard Viewer (Racing API)")
st.write("🔍 Fetching UK race data from The Racing API...")

# Load credentials from Streamlit secrets
if "RACING_API_USERNAME" not in st.secrets or "RACING_API_PASSWORD" not in st.secrets:
    st.error("Missing API credentials.")
    st.stop()

username = st.secrets["RACING_API_USERNAME"]
password = st.secrets["RACING_API_PASSWORD"]

auth_string = f"{username}:{password}"
auth_header = base64.b64encode(auth_string.encode()).decode()

headers = {
    "Authorization": f"Basic {auth_header}"
}

today = datetime.today().strftime("%Y-%m-%d")
endpoint = f"https://api.theracingapi.com/regions/gb/racecards"

st.write(f"📡 Sending header: Basic {auth_header[:30]}...")

try:
    response = requests.get(endpoint, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch data: {response.status_code} - {response.text}")
    else:
        data = response.json()
        if not data.get("racecards"):
            st.warning("No UK races found.")
        else:
            for race in data["racecards"]:
                st.markdown(f"**Course:** {race.get('course')}")
                st.markdown(f"**Race Name:** {race.get('race_name')}")
                st.markdown(f"**Time:** {race.get('off_time')}")
                st.markdown("---")
except Exception as e:
    st.exception(e)
