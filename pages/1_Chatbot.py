import streamlit as st
import requests
from streamlit_chat import message
from uuid import uuid4
import base64
import re
from textblob import TextBlob

# Set up the page
st.set_page_config(page_title="🧠 SerenityMind Chatbot", layout="centered")

# --- Background Setup ---
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

# --- Hugging Face Token ---
API_TOKEN = "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"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# --- Preprocess ---
def clean_text(text):
    text = text.strip()
    text = re.sub(r"\bi[ ]*am\b", "I am", text, flags=re.IGNORECASE)
    text = re.sub(r"im ", "I am ", text, flags=re.IGNORECASE)
    return text

# --- Keyword Override for Sensitive Input ---
CRITICAL_KEYWORDS = {
    "lost my baby": ("grief", "very negative", 9.5),
    "my baby died": ("grief", "very negative", 10),
    "i lost someone": ("grief", "very negative", 9),
    "death": ("grief", "very negative", 9),
}

# --- Hugging Face API ---
def query_huggingface_api(prompt, url):
    try:
        res = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=20)
        return res.json() if res.status_code == 200 else None
    except:
        return None

# --- Model URLs ---
ENDPOINTS = {
    "sentiment": "https://api-inference.huggingface.co/models/nlptown/bert-base-multilingual-uncased-sentiment",
    "emotion": "https://api-inference.huggingface.co/models/SamLowe/roberta-base-go_emotions",
    "intensity": "https://api-inference.huggingface.co/models/finiteautomata/bertweet-base-emotion-intensity",
    "motivator": "https://api-inference.huggingface.co/models/OpenAssistant/oasst-sft-1-pythia-12b"
}

# --- Session Storage ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- UI Header ---
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; background-color: #ffffffcc; padding: 0.8rem 1rem; border-radius: 1rem;">
    <div style="display: flex; align-items: center;">
        <span style="font-size: 2rem;">🤖</span>
        <h3 style="margin-left: 1rem;">SerenityBot <span style='font-size:0.8rem; color:green;'>(online)</span></h3>
    </div>
</div>
""", unsafe_allow_html=True)

# --- User Input ---
raw_input = st.text_input("How are you feeling today?")
user_input = clean_text(raw_input)

if user_input:
    st.session_state.chat_history.append(("user", raw_input))
    with st.spinner("Analyzing your mood..."):

        # Override for known trauma expressions
        for phrase, (emo, senti, intense) in CRITICAL_KEYWORDS.items():
            if phrase in user_input.lower():
                emotion_label, sentiment_label, scaled_intensity = emo, senti, intense
                skip_api = True
                break
        else:
            skip_api = False

        # If no override, use APIs + TextBlob
        if not skip_api:
            blob = TextBlob(user_input)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            sentiment_res = query_huggingface_api(user_input, ENDPOINTS["sentiment"])
            emotion_res = query_huggingface_api(user_input, ENDPOINTS["emotion"])
            intensity_res = query_huggingface_api(user_input, ENDPOINTS["intensity"])

            sentiment_label = sentiment_res[0]["label"] if sentiment_res else ("positive" if polarity > 0 else "negative" if polarity < 0 else "neutral")
            emotion_label = emotion_res[0]["label"] if emotion_res else ("confused" if polarity < -0.2 else "hopeful")
            intensity_score = float(intensity_res[0]["score"]) if intensity_res else abs(polarity)
            scaled_intensity = round(intensity_score * 10, 1)

        # Custom prompt for grief or regular prompt
        if emotion_label == "grief":
            prompt = f"""
            You are a gentle AI therapist. A user has shared they are grieving deeply: '{user_input}'
            Offer comfort first. Say it's okay to feel broken. Then suggest a gentle mental health tool (e.g. breathing, journaling).
            Keep it warm and brief.
            """
        else:
            prompt = f"""
            You are a compassionate mental health chatbot. The user feels {emotion_label} and sentiment is {sentiment_label}, intensity is {scaled_intensity}/10.
            Text: '{user_input}'
            Give an empathetic reply and suggest a mental health activity like gratitude journaling, breathing or 54321 technique.
            Be brief and kind.
            """

        motivator_res = query_huggingface_api(prompt, ENDPOINTS["motivator"])
        generated = motivator_res[0]["generated_text"].strip() if motivator_res and isinstance(motivator_res, list) else "You're not alone. Let's take a few deep breaths together."

        reply = f"""
**🧠 Emotional Insight**

You're feeling **{emotion_label}**, sentiment is **{sentiment_label}**, intensity **{scaled_intensity}/10**.

💬 **My Suggestion**

_"{generated}"_

🔎 *Tip:* Practice **box breathing** – inhale 4s, hold 4s, exhale 4s, hold 4s.
"""
        st.session_state.chat_history.append(("bot", reply))

# --- Display Chat Messages ---
for sender, msg in reversed(st.session_state.chat_history):
    message(msg, is_user=(sender == "user"), key=f"{sender}_{uuid4()}")
