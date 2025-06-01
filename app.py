import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

API_USERNAME = st.secrets["RACING_API_USERNAME"]
API_PASSWORD = st.secrets["RACING_API_PASSWORD"]

st.title("🏇 UK Racecard Viewer (Racing API)")
st.markdown("🔍 Fetching UK tracks with races today...")

auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)

# Step 1: Fetch all UK courses
course_url = "https://api.theracingapi.com/v1/courses?region_codes=gb"
resp = requests.get(course_url, auth=auth)

if resp.status_code != 200:
    st.error(f"❌ Error fetching courses: {resp.status_code} - {resp.text}")
    st.stop()

courses = resp.json().get("courses", [])
if not courses:
    st.warning("No UK courses found.")
    st.stop()

# Step 2: Check which courses have races today
available_today = []
for course in courses:
    cid = course["id"]
    rc_url = f"https://api.theracingapi.com/v1/racecards/by-course/{cid}"
    r = requests.get(rc_url, auth=auth)
    if r.status_code == 200:
        cards = r.json().get("racecards", [])
        if cards:
            available_today.append((course["course"], cid))

if not available_today:
    st.warning("❌ No races scheduled at UK tracks today.")
    st.stop()

# Step 3: Dropdown
course_map = dict(available_today)
track = st.selectbox("Select a UK Track with races today", list(course_map.keys()))
track_id = course_map[track]

st.markdown(f"📅 Fetching races for **{track}**...")

race_url = f"https://api.theracingapi.com/v1/racecards/by-course/{track_id}"
race_resp = requests.get(race_url, auth=auth)

if race_resp.status_code != 200:
    st.error(f"❌ Race fetch failed: {race_resp.status_code} - {race_resp.text}")
    st.stop()

races = race_resp.json().get("racecards", [])
st.success(f"✅ Found {len(races)} races at {track}")

for race in races:
    st.subheader(race.get("race_name", "Unnamed Race"))
    st.write(f"**Off Time:** {race.get('off_time')} | **Distance:** {race.get('distance')} | **Type:** {race.get('race_type')}")
