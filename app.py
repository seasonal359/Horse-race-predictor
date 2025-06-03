
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

auth = f"{username}:{password}"
auth_header = base64.b64encode(auth.encode()).decode()
headers = {"Authorization": f"Basic {auth_header}"}

# --- API Helpers ---
def fetch_meets(date_str):
    url = f"https://api.theracingapi.com/v1/north-america/meets?date={date_str}"
    response = requests.get(url, headers=headers)
    return response.json().get("meets", []) if response.status_code == 200 else []

def fetch_entries(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/entries"
    response = requests.get(url, headers=headers)
    return response.json().get("races", []) if response.status_code == 200 else []

# --- Streamlit UI ---
st.title("🇺🇸 US Thoroughbred Race Viewer (Racing API)")
st.markdown("This app fetches North American race meets and entries via The Racing API.")

date = st.date_input("Select Date", value=datetime.date.today())
date_str = date.strftime("%Y-%m-%d")

meets = fetch_meets(date_str)
if not meets:
    st.warning("No meets found.")
    st.stop()

track_options = {f"{m['track_name']} ({m['country']})": m for m in meets}
selected_label = st.selectbox("Select Track", list(track_options.keys()))
selected_meet = track_options[selected_label]

st.subheader(f"📍 {selected_meet['track_name']} - 🗓 {selected_meet['date']}")
st.write(f"Meet ID: `{selected_meet['meet_id']}` | Country: `{selected_meet['country']}`")

if st.checkbox("Show Race Entries"):
    races = fetch_entries(selected_meet['meet_id'])
    if races:
        for race in races:
            st.markdown(f"### Race {race.get('number')}: {race.get('name')}")
            runners = race.get('runners', [])
            if runners:
                flat_runners = []
                for r in runners:
                    flat_runners.append({
                        "Number": r.get("number"),
                        "Horse": r.get("horse"),
                        "Jockey": r.get("jockey", {}).get("last_name"),
                        "Trainer": r.get("trainer", {}).get("last_name")
                    })
                df = pd.DataFrame(flat_runners)
                st.dataframe(df)
            else:
                st.info("No runners available.")
