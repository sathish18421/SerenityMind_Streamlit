import streamlit as st
import requests
from streamlit_chat import message
from PIL import Image
import base64

# Set app config
st.set_page_config(page_title="🧠 SerenityMind Chatbot", layout="centered")

# Custom background using base64 webp
@st.cache_resource
def get_base64_bg(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(image_path):
    encoded = get_base64_bg(image_path)
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/webp;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
    """, unsafe_allow_html=True)

set_background("assets/background.webp")

# Hugging Face token
API_TOKEN = "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"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Query helper
@st.cache_data(show_spinner=False)
def query_huggingface_api(prompt, mode):
    endpoints = {
        "sentiment": "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english",
        "emotion": "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base",
        "motivator": "https://api-inference.huggingface.co/models/gpt2"
    }
    url = endpoints.get(mode)
    if not url:
        return None

    try:
        response = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=30)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"[ERROR] {mode} API: {e}")
    return None

# Initialize chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat header
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; background-color: #ffffffcc; padding: 0.8rem 1rem; border-radius: 1rem;">
    <div style="display: flex; align-items: center;">
        <span style="font-size: 2rem;">🤖</span>
        <h3 style="margin-left: 1rem;">SerenityBot <span style='font-size:0.8rem; color:green;'>(online)</span></h3>
    </div>
</div>
""", unsafe_allow_html=True)

# Input
user_input = st.text_input("How are you feeling today?")

if user_input:
    st.session_state.chat_history.append(("user", user_input))

    with st.spinner("Analyzing your mood..."):
        sentiment = query_huggingface_api(user_input, "sentiment")
        emotion = query_huggingface_api(user_input, "emotion")

        if sentiment and emotion and isinstance(sentiment, list) and isinstance(emotion, list):
            mood = emotion[0].get("label", "neutral")
            senti = sentiment[0].get("label", "neutral")

            prompt = f"You feel {mood}. Remember,"
            motivational = query_huggingface_api(prompt, "motivator")

            if motivational and isinstance(motivational, list) and "generated_text" in motivational[0]:
                generated = motivational[0]["generated_text"].strip()
            else:
                generated = "You are stronger than you think. Take a deep breath and face the moment with courage."

            reply = f"""
**🧠 Emotional Insight**

You're feeling **{mood.lower()}** and your sentiment is **{senti.lower()}**.

💬 **My Suggestion**

_"{generated}"_

🧘 Mental health tip: Try **Box Breathing** — inhale 4s, hold 4s, exhale 4s, hold 4s. It's a calming technique backed by neuroscience.
"""
        else:
            reply = "😕 Sorry, I couldn't understand your mood. Please try again with more detail or different words."

        st.session_state.chat_history.append(("bot", reply))

# Display messages (corrected key generation)
for idx, (sender, msg) in enumerate(st.session_state.chat_history):
    message(msg, is_user=(sender == "user"), key=f"{sender}_{idx}")
