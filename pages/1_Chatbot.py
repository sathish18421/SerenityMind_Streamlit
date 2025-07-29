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
genai.configure(api_key="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")
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
    with st.spinner("Analyzing your message and crafting a caring response..."):
        blob = TextBlob(user_input)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        # Determine sentiment label
        if polarity > 0.2:
            sentiment_label = "positive"
            emotion_label = "hopeful"
        elif polarity < -0.2:
            sentiment_label = "negative"
            emotion_label = "sad or confused"
        else:
            sentiment_label = "neutral"
            emotion_label = "uncertain or calm"

        scaled_intensity = round(abs(polarity) * 10, 1)

        # Compose detailed prompt for Gemini with empathy + science + advice
        context_prompt = f"""
The user expressed: "{user_input}"

Sentiment analysis details:
- Sentiment: {sentiment_label}
- Emotion: {emotion_label}
- Intensity (0-10): {scaled_intensity}
- Polarity: {polarity:.2f}
- Subjectivity: {subjectivity:.2f}

Instructions:
You are a compassionate therapist and science-backed coach. 
Respond with empathy and emotional insight first, acknowledging the user's feelings.

Then, provide motivational support highlighting positive scientific or psychological facts relevant to their situation.

Finally, suggest practical coping mechanisms or wellness tips, such as journaling, mindfulness, breathing exercises, or reaching out to loved ones.

Use a warm, calm, and encouraging tone. Format your response clearly with:

🧠 Emotional Insight  
💬 Supportive Message  
🔬 Science Tip  
🌱 Wellness Suggestion

Do not repeat the user's input verbatim. Make the reply personal and hopeful.
"""

        response = chat_session.send_message(context_prompt)
        reply_text = response.text.strip()

        reply = f"""
**🧠 Emotional Insight**

You're feeling **{emotion_label}** with a **{sentiment_label}** sentiment, intensity **{scaled_intensity}/10**.

💬 **Supportive Message**

_{reply_text}_

🔎 *Try wellness practices like mindfulness, journaling, or the 5-4-3-2-1 grounding technique.*
"""
        st.session_state.chat_history.append(("bot", reply))

# ------------------ Chat Display ------------------
for sender, msg in reversed(st.session_state.chat_history):
    message(msg, is_user=(sender == "user"), key=f"{sender}_{uuid4()}")
