import streamlit as st
from datetime import datetime
import os

st.set_page_config(page_title="Journal - SerenityMind")
st.title("📝 Daily Journal")

today = datetime.today().strftime("%Y-%m-%d")
journal_file = f"data/journal_{today}.txt"

entry = st.text_area("Write your thoughts for today:", height=300)

if st.button("Save Entry"):
    os.makedirs("data", exist_ok=True)
    with open(journal_file, "w", encoding="utf-8") as f:
        f.write(entry)
    st.success("Journal entry saved!")

if os.path.exists(journal_file):
    with open(journal_file, "r", encoding="utf-8") as f:
        saved = f.read()
    st.subheader("🗂️ Today's Saved Entry")
    st.code(saved)
