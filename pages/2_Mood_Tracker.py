import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

st.set_page_config(page_title="Mood Tracker - SerenityMind")
st.title("📊 Mood Tracker")

moods = ["Happy", "Sad", "Angry", "Anxious", "Calm", "Excited"]
selected_mood = st.radio("How do you feel today?", moods, horizontal=True)
notes = st.text_area("Add any notes about your mood (optional):")

if st.button("Log Mood"):
    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame([[datetime.now(), selected_mood, notes]], columns=["datetime", "mood", "note"])
    df.to_csv("data/mood_log.csv", mode="a", header=not os.path.exists("data/mood_log.csv"), index=False)
    st.success("Mood logged!")

if os.path.exists("data/mood_log.csv"):
    df = pd.read_csv("data/mood_log.csv")
    st.line_chart(df["mood"].value_counts())
    st.dataframe(df.tail(10))
