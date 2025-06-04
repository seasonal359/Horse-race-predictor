
import streamlit as st
import requests
import base64
import datetime
import pandas as pd

# --- Auth Header ---
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")
if not username or not password:
    st.error("Missing API credentials in Streamlit secrets.")
    st.stop()

auth_header = base64.b64encode(f"{username}:{password}".encode()).decode()
headers = { "Authorization": f"Basic {auth_header}" }

# --- Fetch Meets ---
def fetch_meets(date_str):
    url = f"https://api.theracingapi.com/v1/north-america/meets?date={date_str}"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error(f"Failed to fetch meets: {r.status_code} - {r.text}")
        return []
    return r.json().get("meets", [])

# --- Fetch Entries ---
def fetch_entries(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/entries"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error(f"Failed to fetch entries: {r.status_code} - {r.text}")
        return []
    return r.json().get("races", [])

# --- Streamlit UI ---
st.title("🇺🇸 US Thoroughbred Race Viewer (Racing API)")
st.markdown("This app fetches North American race meets and entries via The Racing API.")

date = st.date_input("Select Date", datetime.date.today())
date_str = date.strftime("%Y-%m-%d")

meets = fetch_meets(date_str)
if not meets:
    st.warning("No meets found.")
    st.stop()

track_map = {f"{m['track_name']} ({m['country']})": m for m in meets}
track_label = st.selectbox("Select Track", list(track_map))
meet = track_map[track_label]

st.markdown(f"📍 **{meet['track_name']}** - 🗓 {meet['date']}")
st.code(f"Meet ID: {meet['meet_id']}")

races = fetch_entries(meet['meet_id'])
if not races:
    st.warning("No races found.")
    st.stop()

for race in races:
    st.markdown(f"### Race {race.get('number', 'Unknown')}: {race.get('name', 'Unnamed Race')}")
    runners = race.get("runners", [])
    if not runners:
        st.info("No runners available.")
        continue

    rows = []
    for runner in runners:
        horse = runner.get("horse", "N/A")
        num = runner.get("number", "N/A")
        jockey = runner.get("jockey", {}).get("alias", "N/A")
        trainer = runner.get("trainer", {}).get("alias", "N/A")
        odds = runner.get("odds", {}).get("decimal", "N/A")
        rows.append({
            "Number": num,
            "Horse": horse,
            "Jockey": jockey,
            "Trainer": trainer,
            "Odds": odds
        })

    df = pd.DataFrame(rows)
    st.dataframe(df)
