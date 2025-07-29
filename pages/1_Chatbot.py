import streamlit as st
import requests
from streamlit_chat import message
from uuid import uuid4
import base64
import re
from textblob import TextBlob
import google.generativeai as genai

# ------------------ Streamlit Setup ------------------
st.set_page_config(page_title="🧠 SerenityMind Chatbot", layout="centered")

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

# ------------------ Google Gemini Setup ------------------
genai.configure(api_key="AIzaSyDE64Dbqcf8nGRYqYvN7q8_eWml9bAdrfI")
model = genai.GenerativeModel(model_name="models/gemini-pro")
chat_session = model.start_chat()

# ------------------ Preprocessing ------------------
def clean_text(text):
    text = text.strip()
    text = re.sub(r"\bi[ ]*am\b", "I am", text, flags=re.IGNORECASE)
    text = re.sub(r"im ", "I am ", text, flags=re.IGNORECASE)
    text = text.replace("depressed", "very sad")
    text = text.replace("in depression", "feeling deeply low")
    return text

# ------------------ Chatbot UI ------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; background-color: #ffffffcc; padding: 0.8rem 1rem; border-radius: 1rem;">
    <div style="display: flex; align-items: center;">
        <span style="font-size: 2rem;">🤖</span>
        <h3 style="margin-left: 1rem;">SerenityBot <span style='font-size:0.8rem; color:green;'>(online)</span></h3>
    </div>
</div>
""", unsafe_allow_html=True)

raw_input = st.text_input("How are you feeling today?")
user_input = clean_text(raw_input)

if user_input:
    st.session_state.chat_history.append(("user", raw_input))
    with st.spinner("Analyzing your message and context..."):
        blob = TextBlob(user_input)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        sentiment_label = "positive" if polarity > 0 else "negative" if polarity < 0 else "neutral"
        emotion_label = "confused" if polarity < -0.2 else "hopeful"
        scaled_intensity = round(abs(polarity) * 10, 1)

        context_prompt = f"""
        The user feels {emotion_label}, sentiment is {sentiment_label}, intensity {scaled_intensity}/10.
        TextBlob: polarity={polarity:.2f}, subjectivity={subjectivity:.2f}.
        The user said: '{user_input}'

        Respond like a supportive therapist. Give an empathetic and motivational reply, and suggest a helpful action (e.g., deep breathing, journaling, reaching out to a friend).
        """
        response = chat_session.send_message(context_prompt)
        reply_text = response.text

        reply = f"""
**🧠 Emotional Insight**

You're feeling **{emotion_label}**, sentiment is **{sentiment_label}**, intensity **{scaled_intensity}/10**.

💬 **My Suggestion**

_"{reply_text.strip()}"_

🔎 *Try a wellness tip: mindfulness, journaling, or 54321 grounding.*
"""
        st.session_state.chat_history.append(("bot", reply))

# ------------------ Chat Display ------------------
for sender, msg in reversed(st.session_state.chat_history):
    message(msg, is_user=(sender == "user"), key=f"{sender}_{uuid4()}")
