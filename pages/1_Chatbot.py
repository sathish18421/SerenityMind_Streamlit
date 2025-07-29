import streamlit as st
import requests
from streamlit_chat import message
from PIL import Image
import base64
import re

# Set app config
st.set_page_config(page_title="🧠 SerenityMind Chatbot", layout="centered")

# Preprocess user input
def clean_text(text):
    text = text.strip().lower()
    text = re.sub(r"\bi[ ]*am\b", "I am", text)
    text = text.replace("im ", "I am ")
    text = text.replace("depressed", "sad")
    text = text.replace("in depression", "feeling very sad")
    text = text.replace("low mood", "feeling down")
    return text

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

# Token setup
API_TOKEN = "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"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Helper function for Hugging Face APIs
@st.cache_data(show_spinner=False)
def query_huggingface_api(prompt, mode):
    endpoints = {
        "sentiment": "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english",
        "emotion": "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base",
        "motivator": "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
    }
    url = endpoints.get(mode)
    if not url:
        return None

    response = requests.post(url, headers=headers, json={"inputs": prompt})
    if response.status_code == 200:
        return response.json()
    return None

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chatbot header
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; background-color: #ffffffcc; padding: 0.8rem 1rem; border-radius: 1rem;">
    <div style="display: flex; align-items: center;">
        <span style="font-size: 2rem;">🤖</span>
        <h3 style="margin-left: 1rem;">SerenityBot <span style='font-size:0.8rem; color:green;'>(online)</span></h3>
    </div>
</div>
""", unsafe_allow_html=True)

# User input
raw_input = st.text_input("How are you feeling today?")
user_input = clean_text(raw_input)

if user_input:
    st.session_state.chat_history.append(("user", user_input))

    with st.spinner("Analyzing your mood..."):
        sentiment = query_huggingface_api(user_input, "sentiment")
        emotion = query_huggingface_api(user_input, "emotion")

        st.write("Sentiment Raw:", sentiment)
        st.write("Emotion Raw:", emotion)

        # fallback if result is empty or bad
        if not emotion or not isinstance(emotion, list) or "label" not in emotion[0]:
            emotion = [{"label": "sadness"}]
        if not sentiment or not isinstance(sentiment, list) or "label" not in sentiment[0]:
            sentiment = [{"label": "negative"}]

        mood = emotion[0].get("label", "neutral")
        senti = sentiment[0].get("label", "neutral")
        prompt = f"You are a compassionate AI mental health therapist. The user feels {mood.lower()} and their sentiment is {senti.lower()}. User says: '{user_input}'. Respond with empathy, suggest a helpful mental health technique like box breathing, gratitude journaling, or grounding. Be friendly and brief."
        motivational = query_huggingface_api(prompt, "motivator")

        response_text = motivational[0]['generated_text'].strip() if motivational and isinstance(motivational, list) else "Let's take a deep breath and move forward together."

        reply = f"""
**🧠 Emotional Insight**

You're feeling **{mood.lower()}** and your sentiment is **{senti.lower()}**.

💬 **My Suggestion**

_"{response_text}"_

🔎 Try this tip: **Box breathing** – inhale 4s, hold 4s, exhale 4s, hold 4s. A quick calm-down technique backed by neuroscience!
"""
        st.session_state.chat_history.append(("bot", reply))

# Chat UI
for i, (sender, msg) in enumerate(reversed(st.session_state.chat_history)):
    message(msg, is_user=(sender == "user"), key=f"{sender}_{i}_{abs(hash(msg))}")
