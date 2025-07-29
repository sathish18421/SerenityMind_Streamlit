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
    if not text:
        return ""
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
def query_huggingface_api(prompt, url):
    response = requests.post(url, headers=headers, json={"inputs": prompt})
    if response.status_code == 200:
        try:
            return response.json()
        except:
            return None
    return None

# Model endpoints
ENDPOINTS = {
    "sentiment": "https://api-inference.huggingface.co/models/nlptown/bert-base-multilingual-uncased-sentiment",
    "emotion": "https://api-inference.huggingface.co/models/SamLowe/roberta-base-go_emotions",
    "intensity": "https://api-inference.huggingface.co/models/finiteautomata/bertweet-base-emotion-intensity",
    "motivator": "https://api-inference.huggingface.co/models/OpenAssistant/oasst-sft-1-pythia-12b"
}

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
    st.session_state.chat_history.append(("user", raw_input))

    with st.spinner("Analyzing your mood..."):
        sentiment_res = query_huggingface_api(user_input, ENDPOINTS["sentiment"])
        emotion_res = query_huggingface_api(user_input, ENDPOINTS["emotion"])
        intensity_res = query_huggingface_api(user_input, ENDPOINTS["intensity"])

        # Safely extract data
        try:
            senti_label = sentiment_res[0]['label'] if sentiment_res else "neutral"
            emotion_label = emotion_res[0]['label'] if emotion_res else "neutral"
            intensity_score = float(intensity_res[0]['score']) if intensity_res else 0.5
        except Exception:
            senti_label = "neutral"
            emotion_label = "neutral"
            intensity_score = 0.5

        scaled_intensity = round(intensity_score * 10, 1)

        prompt = f"""
        You are a compassionate mental health AI. The user is feeling {emotion_label.lower()} with an emotional intensity of {scaled_intensity}/10 and sentiment is {senti_label.lower()}. They said: '{user_input}'.
        Reply empathetically. Suggest one mental wellness tip like gratitude journaling, box breathing, or 5-4-3-2-1 grounding. Keep it short and warm.
        """
        motivational_res = query_huggingface_api(prompt, ENDPOINTS["motivator"])
        if motivational_res and isinstance(motivational_res, list):
            response_text = motivational_res[0]['generated_text'].strip()
        else:
            response_text = "You are not alone. Let's try a grounding technique together."

        reply = f"""
**🧠 Emotional Insight**

You're feeling **{emotion_label.lower()}** with an emotional intensity of **{scaled_intensity}/10** and your sentiment is **{senti_label.lower()}**.

💬 **My Suggestion**

_"{response_text}"_

🔎 Tip: Try **box breathing** – inhale 4s, hold 4s, exhale 4s, hold 4s. Used by therapists and elite performers!
"""
        st.session_state.chat_history.append(("bot", reply))

# Chat UI
for i, (sender, msg) in enumerate(reversed(st.session_state.chat_history)):
    message(msg, is_user=(sender == "user"), key=f"{sender}_{i}")
