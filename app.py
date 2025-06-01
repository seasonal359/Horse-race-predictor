# Horse Race Predictor using rpscrape (Racing Post) for US Tracks

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score
import datetime
import joblib
import streamlit as st
import logging

from rpscrape import RP

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)

# --- Step 1: Load RPScrape Data for US Tracks ---
def get_rps_data(date_str):
    try:
        rp = RP()
        all_races = rp.get_racecards(date=date_str)
        us_races = [race for race in all_races if "USA" in race.get("country", "") or "United States" in race.get("country", "")]
        return us_races
    except Exception as e:
        logging.exception("Error fetching racecards from rpscrape")
        return []

# --- Helper: Get Horses from Race ID ---
def get_race_horses(race_id):
    try:
        rp = RP()
        race = rp.get_racecard(race_id)
        return race.get("horses", [])
    except Exception as e:
        logging.exception("Error fetching race details")
        return []

# --- Step 2: Load Sample Training Data ---
def load_training_data():
    data = pd.DataFrame({
        'odds': np.random.uniform(1, 20, 200),
        'horse_age': np.random.randint(2, 10, 200),
        'jockey_win_rate': np.random.uniform(0.1, 0.5, 200),
        'track_condition_num': np.random.choice([1, 2, 3, 4], 200),
        'distance': np.random.choice([1000, 1200, 1400, 1600], 200),
        'pace': np.random.uniform(75, 100, 200),
        'speed': np.random.uniform(80, 105, 200),
        'class_rating': np.random.uniform(70, 100, 200),
        'position': np.random.randint(1, 10, 200)
    })
    data['win'] = (data['position'] == 1).astype(int)
    return data

# --- Step 3: Train Model ---
track_map = {'Fast': 1, 'Good': 2, 'Sloppy': 3, 'Wet': 4}
data = load_training_data()
features = ['odds', 'horse_age', 'jockey_win_rate', 'track_condition_num', 'distance', 'pace', 'speed', 'class_rating']
X = data[features]
y = data['win']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
base_model = RandomForestClassifier(n_estimators=100, random_state=42)
model = CalibratedClassifierCV(base_model, method='sigmoid', cv=3)
model.fit(X_train, y_train)
joblib.dump(model, "model.pkl")
model = joblib.load("model.pkl")
preds = model.predict(X_test)
acc = accuracy_score(y_test, preds)

# --- Streamlit Interface ---
st.title("🏇 Horse Race Predictor (US Races via RPScrape)")
st.sidebar.header("Select Date and Race")

race_date = st.sidebar.text_input("Race Date (YYYY-MM-DD)", datetime.datetime.today().strftime("%Y-%m-%d"))
all_races = get_rps_data(race_date)

if not all_races:
    st.warning("No US races found for this date.")
else:
    race_options = {f"{r['track']} - Race {r['race_number']} @ {r['off_time']}": r['race_id'] for r in all_races}
    selected_race = st.sidebar.selectbox("Select Race", list(race_options.keys()))
    race_id = race_options[selected_race]

    horses = get_race_horses(race_id)
    if not horses:
        st.warning("No horses found in selected race.")
    else:
        st.write(f"Model accuracy on test set: {acc:.2f}")
        df = pd.DataFrame([{
            "name": h.get("name", "Unknown"),
            "odds": h.get("odds_decimal", np.random.uniform(3, 15)),
            "jockey": h.get("jockey", "Unknown"),
            "horse_age": h.get("age", np.random.randint(3, 7)),
            "jockey_win_rate": np.random.uniform(0.15, 0.35),
            "track_condition_num": track_map.get("Fast", 1),
            "distance": np.random.choice([1000, 1200, 1400, 1600]),
            "pace": np.random.uniform(80, 95),
            "speed": np.random.uniform(85, 100),
            "class_rating": np.random.uniform(75, 90)
        } for h in horses])

        df['win_prob'] = model.predict_proba(df[features])[:, 1]
        df['ROI_est'] = (df['win_prob'] * df['odds']).round(2)
        st.dataframe(df[['name', 'odds', 'jockey', 'win_prob', 'ROI_est', 'pace', 'speed', 'class_rating']].sort_values("ROI_est", ascending=False))
