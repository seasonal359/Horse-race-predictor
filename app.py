
import streamlit as st
import datetime

st.set_page_config(page_title="Debug - Streamlit Up", layout="centered")
st.title("🇺🇸 Racing API Debug")
st.markdown("This debug app ensures Streamlit is rendering properly.")

st.success("✅ Streamlit is working!")

date = st.date_input("Pick a date", value=datetime.date.today())
st.info(f"You picked: {date}")
