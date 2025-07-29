import streamlit as st
import time

st.set_page_config(page_title="Self-Care - SerenityMind")
st.title("🧘 Self-Care Center")

option = st.selectbox("Choose a self-care activity", ["Breathing Exercise", "Daily Affirmation", "Relaxing Sound"])

if option == "Breathing Exercise":
    st.subheader("🌬️ Breathing Animation")
    st.markdown("**Inhale... Hold... Exhale...**")
    for i in range(3):
        st.info("🫁 Inhale...")
        time.sleep(3)
        st.success("✋ Hold...")
        time.sleep(2)
        st.warning("💨 Exhale...")
        time.sleep(4)
elif option == "Daily Affirmation":
    st.success("🌟 You are doing your best, and that is enough.")
elif option == "Relaxing Sound":
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
