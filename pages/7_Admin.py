import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Admin Dashboard - SerenityMind")
st.title("📊 Admin Dashboard")

if os.path.exists("data/mood_log.csv"):
    st.subheader("Mood Trends")
    df = pd.read_csv("data/mood_log.csv")
    st.line_chart(df["mood"].value_counts())

    st.subheader("Recent Mood Entries")
    st.dataframe(df.tail(10))

    st.download_button("Download All Mood Logs", data=df.to_csv(index=False), file_name="mood_data.csv")
else:
    st.info("No data yet. Ask users to log moods.")
