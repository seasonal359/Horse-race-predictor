
import streamlit as st
import requests
import base64
import os

st.title("🇬🇧 UK Racecard Viewer (Racing API)")
st.write("🔍 Fetching UK race data from The Racing API...")

# Read secrets from Streamlit
username = st.secrets.get("username")
password = st.secrets.get("password")

if not username or not password:
    st.error("Missing API credentials.")
else:
    credentials = f"{username}:{password}"
    auth_header = base64.b64encode(credentials.encode()).decode()
    st.write(f"📡 Sending header: Basic {auth_header[:30]}...")

    url = "https://api.theracingapi.com/v1/racecards"
    headers = {
        "Authorization": f"Basic {auth_header}"
    }
    params = {
        "region_codes": "gb"
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        st.error(f"Failed to fetch data: {response.status_code} - {response.text}")
    else:
        data = response.json()
        racecards = data.get("racecards", [])
        if not racecards:
            st.warning("No UK races found today.")
        else:
            for race in racecards:
                st.subheader(race.get("race_name", "Unnamed Race"))
                st.markdown(f"**Course:** {race.get('course')}  
"
                            f"**Off Time:** {race.get('off_time')}  
"
                            f"**Type:** {race.get('type')}  
"
                            f"**Distance:** {race.get('distance')}  
"
                            f"**Going:** {race.get('going')}")
