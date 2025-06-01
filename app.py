import streamlit as st
import requests
from requests.auth import _basic_auth_str

# Load credentials
API_USERNAME = st.secrets["RACING_API_USERNAME"]
API_PASSWORD = st.secrets["RACING_API_PASSWORD"]

st.title("🏇 UK Racecourse Lookup (Racing API)")
st.markdown("🔍 Fetching UK racecourses from The Racing API...")

auth_header = _basic_auth_str(API_USERNAME, API_PASSWORD)
st.text(f"📡 Sending header: {auth_header[:30]}...")

headers = {
    "Authorization": auth_header
}

api_url = "https://api.theracingapi.com/v1/courses?region_codes=gb"

response = requests.get(api_url, headers=headers)

if response.status_code == 200:
    courses = response.json().get("courses", [])
    if not courses:
        st.warning("No UK racecourses found.")
        st.subheader("🔎 Raw API Response:")
        st.json(response.json())
    else:
        st.success(f"✅ Found {len(courses)} UK racecourses.")
        df = [{ "Course": c["course"], "Region": c["region"], "ID": c["course_id"] } for c in courses]
        st.dataframe(df)
else:
    st.error(f"Failed to fetch courses: {response.status_code} - {response.text}")
