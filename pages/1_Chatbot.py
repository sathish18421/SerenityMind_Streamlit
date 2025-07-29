import streamlit as st
import requests
from streamlit_chat import message
from uuid import uuid4
import base64
import re

# Page config
st.set_page_config(page_title="🧠 SerenityMind Chatbot", layout="centered")

# Background Setup
@st.cache_resource
def get_base64_bg(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

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

# Preprocessing
def clean_text(text):
    text = text.strip().lower()
    text = re.sub(r"\bi[ ]*am\b", "I am", text)
    text = text.replace("im ", "I am ")
    text = text.replace("depressed", "very sad")
    text = text.replace("in depression", "feeling deeply low")
    return text

# Hugging Face API query
def query_huggingface_api(prompt, url):
    try:
        res = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=15)
        return res.json() if res.status_code == 200 else None
    except:
        return None

# Models
ENDPOINTS = {
    "sentiment": "https://api-inference.huggingface.co/models/nlptown/bert-base-multilingual-uncased-sentiment",
    "emotion": "https://api-inference.huggingface.co/models/SamLowe/roberta-base-go_emotions",
    "intensity": "https://api-inference.huggingface.co/models/finiteautomata/bertweet-base-emotion-intensity",
    "motivator": "https://api-inference.huggingface.co/models/OpenAssistant/oasst-sft-1-pythia-12b"
}

# Session history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Header
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; background-color: #ffffffcc; padding: 0.8rem 1rem; border-radius: 1rem;">
    <div style="display: flex; align-items: center;">
        <span style="font-size: 2rem;">🤖</span>
        <h3 style="margin-left: 1rem;">SerenityBot <span style='font-size:0.8rem; color:green;'>(online)</span></h3>
    </div>
</div>
""", unsafe_allow_html=True)

# Input
raw_input = st.text_input("How are you feeling today?")
user_input = clean_text(raw_input)

if user_input:
    st.session_state.chat_history.append(("user", raw_input))
    with st.spinner("Analyzing..."):
        # Sentiment
        sentiment_res = query_huggingface_api(user_input, ENDPOINTS["sentiment"])
        sentiment_label = sentiment_res[0]["label"] if sentiment_res else "neutral"

        # Emotion
        emotion_res = query_huggingface_api(user_input, ENDPOINTS["emotion"])
        emotion_label = emotion_res[0]["label"] if emotion_res else "unidentified emotion"

        # Intensity
        intensity_res = query_huggingface_api(user_input, ENDPOINTS["intensity"])
        intensity_score = float(intensity_res[0]["score"]) if intensity_res else 0.5
        scaled_intensity = round(intensity_score * 10, 1)

        # Prompt for motivation
        prompt = f"""
        You are a caring AI therapist. The user is feeling {emotion_label} with sentiment {sentiment_label} at {scaled_intensity}/10 intensity. They said: '{user_input}'.
        Respond with empathy. Then suggest a simple, research-backed mental health technique (e.g. gratitude, box breathing, 54321 method).
        Be kind, short, and warm.
        """
        motivator_res = query_huggingface_api(prompt, ENDPOINTS["motivator"])
        generated = motivator_res[0]["generated_text"].strip() if motivator_res and isinstance(motivator_res, list) else "You're not alone. Let's try a mindful breathing exercise together."

        reply = f"""
**🧠 Emotional Insight**

You're feeling **{emotion_label}**, sentiment is **{sentiment_label}**, and intensity is **{scaled_intensity}/10**.

💬 **My Suggestion**

_"{generated}"_

🔎 *Tip:* Try **54321 grounding** – Name 5 things you see, 4 you feel, 3 you hear, 2 you smell, 1 you taste.
"""
        st.session_state.chat_history.append(("bot", reply))

# Display
for sender, msg in reversed(st.session_state.chat_history):
    message(msg, is_user=(sender == "user"), key=f"{sender}_{uuid4()}")
