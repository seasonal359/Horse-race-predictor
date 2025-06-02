import streamlit as st
import requests
import base64
from datetime import datetime

st.set_page_config(page_title="🇺🇸 US Race Viewer (Racing API)", layout="centered")
st.title("🇺🇸 US Thoroughbred Race Viewer (Racing API)")

# --- Load API credentials from Streamlit secrets ---
try:
    username = st.secrets["racing_api"]["username"]
    password = st.secrets["racing_api"]["password"]
except Exception:
    st.error("Missing API credentials in Streamlit secrets.")
    st.stop()

# --- Create Authorization Header ---
auth_string = f"{username}:{password}"
auth_header = base64.b64encode(auth_string.encode()).decode()
headers = {
    "Authorization": f"Basic {auth_header}"
}

# --- Step 1: List today's North American meets ---
st.markdown("🔍 Fetching today's race meets from The Racing API...")
today = datetime.today().strftime('%Y-%m-%d')
meets_url = f"https://api.theracingapi.com/v1/north-america/meets?date={today}"

resp = requests.get(meets_url, headers=headers)
if resp.status_code != 200:
    st.error(f"Failed to fetch meets: {resp.status_code} - {resp.text}")
    st.stop()

meets = resp.json().get("meets", [])
if not meets:
    st.warning("❌ No North American race meets found today.")
    st.stop()

meet_map = {f"{m['track_name']} ({m['track_code']})": m["id"] for m in meets}
selected_meet = st.selectbox("Select a Race Meet", list(meet_map.keys()))
meet_id = meet_map[selected_meet]

# --- Step 2: Fetch entries for selected meet ---
entries_url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/entries"
st.markdown(f"📅 Fetching race entries for **{selected_meet}**...")
resp_entries = requests.get(entries_url, headers=headers)

if resp_entries.status_code != 200:
    st.error(f"Failed to fetch race entries: {resp_entries.status_code} - {resp_entries.text}")
    st.stop()

entries = resp_entries.json().get("races", [])
if not entries:
    st.warning("❌ No races or entries available for this meet.")
    st.stop()

# --- Step 3: Display races and horses ---
for race in entries:
    st.subheader(f"Race {race['race_number']}: {race.get('race_name', 'No Title')}")
    st.markdown(f"**Post Time:** {race.get('post_time_local', 'TBD')}")
    horses = race.get("runners", [])
    if not horses:
        st.write("No runners found.")
        continue
    rows = []
    for h in horses:
        rows.append({
            "Horse": h["name"],
            "Jockey": h.get("jockey_name", "N/A"),
            "Trainer": h.get("trainer_name", "N/A"),
            "Odds": h.get("morning_line", "N/A")
        })
    st.dataframe(rows)
