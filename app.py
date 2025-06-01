import streamlit as st
import requests
from requests.auth import _basic_auth_str
from datetime import datetime

# Load credentials
API_USERNAME = st.secrets["RACING_API_USERNAME"]
API_PASSWORD = st.secrets["RACING_API_PASSWORD"]

st.title("🏇 UK Racecard Viewer (Racing API)")
st.markdown("🔍 Pulling UK racecourses and live racecards...")

auth_header = _basic_auth_str(API_USERNAME, API_PASSWORD)
headers = { "Authorization": auth_header }

# Step 1: Fetch all UK racecourses
course_url = "https://api.theracingapi.com/v1/courses?region_codes=gb"
response = requests.get(course_url, headers=headers)

if response.status_code != 200:
    st.error(f"Failed to load courses: {response.status_code} - {response.text}")
    st.stop()

courses = response.json().get("courses", [])
if not courses:
    st.warning("No courses found.")
    st.stop()

# Dropdown to select course
course_map = {course["course"]: course["id"] for course in courses}
selected_course = st.selectbox("Select a UK Racecourse", list(course_map.keys()))
course_id = course_map[selected_course]

# Step 2: Fetch racecards for selected course
racecard_url = f"https://api.theracingapi.com/v1/racecards?course_id={course_id}"
st.markdown(f"📅 Fetching races for **{selected_course}**")

race_response = requests.get(racecard_url, headers=headers)

if race_response.status_code != 200:
    st.error(f"Failed to fetch racecards: {race_response.status_code} - {race_response.text}")
    st.stop()

racecards = race_response.json().get("racecards", [])

if not racecards:
    st.warning(f"No races found for {selected_course}.")
    st.json(race_response.json())
else:
    st.success(f"✅ Found {len(racecards)} races.")
    for race in racecards:
        st.subheader(race.get("race_name", "Unnamed Race"))
        st.write(f"**Off Time:** {race.get('off_time')} | **Distance:** {race.get('distance')} | **Region:** {race.get('region')}")
