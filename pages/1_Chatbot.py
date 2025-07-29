import streamlit as st
import requests
from streamlit_chat import message
from uuid import uuid4
import base64
import re
from textblob import TextBlob

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
    text = text.strip()
    text = re.sub(r"\bi[ ]*am\b", "I am", text, flags=re.IGNORECASE)
    text = re.sub(r"im ", "I am ", text, flags=re.IGNORECASE)
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
    with st.spinner("Analyzing your mood..."):
        # TextBlob sentiment
        blob = TextBlob(user_input)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        # Hugging Face Models
        sentiment_res = query_huggingface_api(user_input, ENDPOINTS["sentiment"])
        emotion_res = query_huggingface_api(user_input, ENDPOINTS["emotion"])
        intensity_res = query_huggingface_api(user_input, ENDPOINTS["intensity"])

        sentiment_label = sentiment_res[0]["label"] if sentiment_res else ("positive" if polarity > 0 else "negative" if polarity < 0 else "neutral")
        emotion_label = emotion_res[0]["label"] if emotion_res else ("confused" if polarity < -0.2 else "hopeful")
        intensity_score = float(intensity_res[0]["score"]) if intensity_res else abs(polarity)
        scaled_intensity = round(intensity_score * 10, 1)

        # Prompt for motivation
        prompt = f"""
        You are a compassionate AI therapist. The user feels {emotion_label}, sentiment is {sentiment_label}, intensity {scaled_intensity}/10. 
        TextBlob analysis: polarity={polarity:.2f}, subjectivity={subjectivity:.2f}.
        They said: '{user_input}'
        Give a brief empathetic response and suggest a helpful mental wellness activity like gratitude journaling, deep breathing, or grounding.
        """
        motivator_res = query_huggingface_api(prompt, ENDPOINTS["motivator"])
        generated = motivator_res[0]["generated_text"].strip() if motivator_res and isinstance(motivator_res, list) else "You're not alone. Let's try a mindful breathing exercise together."

        reply = f"""
**🧠 Emotional Insight**

You're feeling **{emotion_label}**, sentiment is **{sentiment_label}**, intensity **{scaled_intensity}/10**.

💬 **My Suggestion**

_"{generated}"_

🔎 *Tip:* Try **box breathing** – inhale 4s, hold 4s, exhale 4s, hold 4s.
"""
        st.session_state.chat_history.append(("bot", reply))

# Display
for sender, msg in reversed(st.session_state.chat_history):
    message(msg, is_user=(sender == "user"), key=f"{sender}_{uuid4()}")
