import streamlit as st
import requests
import base64
import datetime
import json

st.title("🏇 Racing API Debug - Meets Only")

# Load credentials from Streamlit secrets
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")

if not username or not password:
    st.error("Missing credentials in Streamlit secrets.")
    st.stop()

# Prepare auth header
auth_str = f"{username}:{password}"
auth_header = base64.b64encode(auth_str.encode()).decode()
headers = {
    "Authorization": f"Basic {auth_header}"
}

# Date selector
selected_date = st.date_input("Select Date", value=datetime.date.today())
date_str = selected_date.strftime("%Y-%m-%d")

# Fetch meets
st.markdown("📡 Sending request to `/meets`...")
url = f"https://api.theracingapi.com/v1/north-america/meets?date={date_str}"
st.code(f"GET {url}")
st.code(f"Headers: {headers}", language="json")

response = requests.get(url, headers=headers)

st.markdown(f"**Status:** {response.status_code}")
if response.status_code != 200:
    st.error(f"Failed to fetch data: {response.text}")
else:
    meets_data = response.json()
    st.markdown("### Raw API Response")
    st.json(meets_data)

    # Optional: tabulate the meets
    if "meets" in meets_data and meets_data["meets"]:
        meets = meets_data["meets"]
        options = [f"{m['track_name']} ({m['country']}) — {m['date']}" for m in meets]
        selected_meet = st.selectbox("Select a Meet", options)
    else:
        st.warning("No meets returned.")
