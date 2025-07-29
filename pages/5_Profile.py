import streamlit as st

st.set_page_config(page_title="Profile - SerenityMind")
st.title("👤 User Profile")

name = st.text_input("Name")
age = st.slider("Age", 10, 100, 25)
goals = st.text_area("What are your current life goals?")
avatar = st.radio("Choose an avatar", ["🌞", "🌸", "🦋", "🌻"])

if st.button("Save Profile"):
    st.success("Profile saved!")

st.markdown("### 🔍 Your Preferences")
st.write(f"Name: {name}")
st.write(f"Age: {age}")
st.write(f"Goals: {goals}")
st.write(f"Avatar: {avatar}")
