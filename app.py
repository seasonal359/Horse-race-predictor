
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import base64
import os

st.set_page_config(page_title="UK Racecard Viewer (Racing API)")
st.title("🇬🇧 UK Racecard Viewer (Racing API)")

# --- Load credentials from environment (must be set in Streamlit secrets or locally) ---
username = os.getenv("RACING_API_USER")
password = os.getenv("RACING_API_PASS")

if not username or not password:
    st.error("Missing API credentials.")
    st.stop()

# --- Basic Auth Header ---
auth_str = f"{username}:{password}"
auth_bytes = auth_str.encode("utf-8")
auth_b64 = base64.b64encode(auth_bytes).decode("utf-8")
headers = {"Authorization": f"Basic {auth_b64}"}

# --- Helper: Fetch all UK racecourses ---
def get_uk_courses():
    url = "https://api.theracingapi.com/v1/courses"
    params = {"region_codes": "gb"}
    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        st.error(f"Failed to fetch UK courses: {res.status_code} - {res.text}")
        return []
    return res.json().get("courses", [])

# --- Helper: Fetch racecards by course ID and date ---
def get_racecard(course_id, date):
    url = f"https://api.theracingapi.com/v1/racecards"
    params = {"course_ids": course_id, "date": date}
    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        st.error(f"Failed to fetch racecards: {res.status_code} - {res.text}")
        return []
    return res.json().get("racecards", [])

# --- UI Flow ---
st.markdown("🔍 Pulling UK racecourses and live racecards...")

courses = get_uk_courses()
if not courses:
    st.stop()

course_names = {c["course"]: c["id"] for c in courses}
selected_course = st.selectbox("Select a UK Racecourse", list(course_names.keys()))

# Allow date selection: today or yesterday for testing
today = datetime.today()
yesterday = today - timedelta(days=1)
race_date = st.radio("Select date", [today.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d")], index=0)

if st.button("Fetch Racecard"):
    st.markdown(f"📅 Fetching races for **{selected_course}** on `{race_date}`...")
    course_id = course_names[selected_course]
    racecards = get_racecard(course_id, race_date)

    if not racecards:
        st.warning("No racecards found for this course and date.")
    else:
        for race in racecards:
            st.subheader(f'🏁 {race["race_name"]} @ {race["off_time"]} - {race["distance"]}')
            st.caption(f'Age: {race.get("age_band", "-")}, Rating: {race.get("rating_band", "-")}, Type: {race["type"]}, Surface: {race.get("surface", "-")}')

            runners = race.get("runners", [])
            if not runners:
                st.text("No runners listed.")
                continue

            df = pd.DataFrame([{
                "Horse": r["horse"],
                "Age": r["age"],
                "Jockey": r["jockey"],
                "Trainer": r["trainer"],
                "Draw": r["draw"],
                "Form": r["form"],
                "RPR": r["rpr"],
                "TS": r["ts"],
                "Comment": r["comment"]
            } for r in runners])
            st.dataframe(df)
