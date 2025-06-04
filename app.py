
# 🏇 Exotic Wagering Overlay Dashboard - Real-Time (Exacta, Trifecta, Superfecta)
import streamlit as st
import requests
import base64
import pandas as pd
import datetime

# --- Auth Setup from Streamlit Secrets ---
username = st.secrets.get("RACING_API_USERNAME")
password = st.secrets.get("RACING_API_PASSWORD")

if not username or not password:
    st.error("Missing Racing API credentials in Streamlit secrets.")
    st.stop()

auth_header = {
    "Authorization": "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode()
}

# --- Fetch Today's Meets from Racing API (North America Add-On) ---
@st.cache_data(ttl=300)
def get_meets(date):
    url = f"https://api.theracingapi.com/v1/north-america/meets?date={date}"
    r = requests.get(url, headers=auth_header)
    if r.status_code != 200:
        return []
    return r.json().get("meets", [])

# --- Fetch Entries for a Meet ---
def get_entries(meet_id):
    url = f"https://api.theracingapi.com/v1/north-america/meets/{meet_id}/entries"
    r = requests.get(url, headers=auth_header)
    if r.status_code != 200:
        return []
    return r.json().get("races", [])

# --- UI ---
st.title("🎯 Exotic Wagering Overlay Dashboard")
st.markdown("Targeting mispriced **Exacta**, **Trifecta**, and **Superfecta** pools at top U.S. tracks.")

target_tracks = ["Saratoga", "Laurel Park", "Churchill Downs"]
selected_date = st.date_input("Select Race Date", value=datetime.date.today())
date_str = selected_date.strftime("%Y-%m-%d")

# --- Fetch Meets ---
with st.spinner("Fetching available meets..."):
    meets = get_meets(date_str)
    meets = [m for m in meets if m["track_name"] in target_tracks]

if not meets:
    st.warning("No valid meets found for selected date and tracks.")
    st.stop()

track_options = {f'{m["track_name"]} ({m["country"]})': m for m in meets}
selected_label = st.selectbox("Select Track", list(track_options.keys()))
selected_meet = track_options[selected_label]

# --- Fetch Races and Entries ---
st.subheader(f"📍 {selected_meet['track_name']} on {selected_meet['date']}")
races = get_entries(selected_meet["meet_id"])

if not races:
    st.warning("No race entries found.")
    st.stop()

# --- Simple ROI Model Placeholder ---
def estimate_overlay(race):
    if "runners" not in race or not race["runners"]:
        return []
    df = pd.DataFrame(race["runners"])
    df["implied_prob"] = 1 / (df["morning_line_odds"].replace(0, 99))  # Placeholder
    df["ROI_flag"] = df["implied_prob"] < 0.10
    return df[df["ROI_flag"] == True][["number", "horse", "jockey", "trainer", "morning_line_odds"]]

# --- Display Races ---
for race in races:
    st.markdown(f"### Race {race.get('number') or 'Unknown'}: {race.get('name') or 'Unnamed'}")
    try:
        overlay_df = estimate_overlay(race)
        if not overlay_df.empty:
            st.success("💡 Potential Overlay Picks Found:")
            st.dataframe(overlay_df)
        else:
            st.info("No overlays found for this race.")
    except Exception as e:
        st.error(f"Failed to process race data: {e}")
