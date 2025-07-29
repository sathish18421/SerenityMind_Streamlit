import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(page_title="SerenityMind 🧠", layout="wide")

with st.sidebar:
    selected = option_menu("SerenityMind", 
        ["Chatbot", "Mood Tracker", "Journal", "Self-Care", "Profile", "Community", "Admin"],
        icons=['chat-dots', 'emoji-smile', 'book', 'heart', 'person-circle', 'people', 'bar-chart'],
        menu_icon="brain", default_index=0)

st.markdown(f"# Welcome to SerenityMind 🧘")
st.info("Select a module from the sidebar to begin.")
