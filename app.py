
import streamlit as st
import requests
import base64
import datetime
import pandas as pd

st.title("🇺🇸 US Thoroughbred Race Viewer (Racing API)")
st.markdown("This app fetches North American race meets and entries via The Racing API.")

# --- Load credentials ---
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")

if not username or not password:
    st.error("Missing API credentials in Streamlit secrets.")
    st.stop()

# --- Build auth headers ---
auth = f"{username}:{password}"
auth_header = base64.b64encode(auth.encode()).decode()
headers = {"Authorization": f"Basic {auth_header}"}

# --- Fetch meets ---
def fetch_meets(date_str):
    url = f"https://api.theracingapi.com/v1/north-america/meets?date={date_str}"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error(f"Failed to fetch meets: {r.status_code} - {r.text}")
        return []
    return r.json().get("meets", [])

# --- Fetch entries for a meet ---
def fetch_entries(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/entries"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error(f"Failed to fetch entries: {r.status_code} - {r.text}")
        return []
    return r.json().get("races", [])

# --- App body ---
date = st.date_input("Select Date", value=datetime.date.today())
date_str = date.strftime("%Y-%m-%d")

meets = fetch_meets(date_str)
if not meets:
    st.warning("No meets found.")
    st.stop()

track_map = {f"{m['track_name']} ({m['country']})": m for m in meets}
track_choice = st.selectbox("Select Track", list(track_map.keys()))
selected_meet = track_map[track_choice]

st.markdown(f"📍 **{selected_meet['track_name']}** - 🗓 {selected_meet['date']}")
st.code(f"Meet ID: {selected_meet['meet_id']} | Country: {selected_meet['country']}")

# --- Show entries ---
races = fetch_entries(selected_meet["meet_id"])
for race in races:
    st.subheader(f"Race {race.get('number', 'Unknown')}: {race.get('name', 'Unnamed Race')}")
    runners = race.get("runners", [])
    data = []
    for runner in runners:
        data.append({
            "Number": runner.get("number", "N/A"),
            "Horse": runner.get("horse", "N/A"),
            "Jockey": runner.get("jockey", {}).get("alias", "N/A") if isinstance(runner.get("jockey"), dict) else "N/A",
            "Trainer": runner.get("trainer", {}).get("alias", "N/A") if isinstance(runner.get("trainer"), dict) else "N/A",
            "Odds": runner.get("odds", "N/A")
        })
    st.dataframe(pd.DataFrame(data))
