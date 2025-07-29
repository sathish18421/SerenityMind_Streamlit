import streamlit as st
from transformers import pipeline
from streamlit_chat import message
import random

# -------------------- Page Setup --------------------
st.set_page_config(page_title="SerenityMind Chatbot", page_icon="🧠", layout="centered")
st.markdown("""
    <style>
    .st-emotion-cache-1v0mbdj {visibility: hidden;} /* Hide default footer */
    .message-bubble {
        background-color: #e8f0fe;
        padding: 1em;
        border-radius: 12px;
        margin-bottom: 0.5em;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("## 🤖 SerenityMind Chatbot")
st.markdown("<span style='color:green;'>🟢 Online</span> &nbsp; | &nbsp; *Your personal AI mental health companion*", unsafe_allow_html=True)
st.write("___")

# -------------------- Model Loading --------------------
@st.cache_resource
def load_models():
    sentiment_model = pipeline("sentiment-analysis")
    emotion_model = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
    motivator = pipeline("text-generation", model="gpt2")
    return sentiment_model, emotion_model, motivator

sentiment_model, emotion_model, motivator = load_models()

# -------------------- Session State --------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "mood_score" not in st.session_state:
    st.session_state.mood_score = None

# -------------------- Mood Selection --------------------
with st.sidebar:
    st.header("🌈 Mood Check-In")
    mood_emoji = st.radio("Choose your mood today:", ["😊 Happy", "😔 Sad", "😠 Angry", "😨 Anxious", "😐 Neutral"])
    st.session_state.mood_score = st.slider("Rate your mood (1 = Worst, 10 = Best):", 1, 10, 5)

# -------------------- Prompt Builder --------------------
def build_prompt(user_input, emotion, sentiment, mood_emoji, mood_score):
    techniques = [
        "deep breathing", "journaling", "talking to a friend", "grounding technique", 
        "5-4-3-2-1 sensory method", "positive affirmations", "taking a short walk", 
        "gratitude listing", "progressive muscle relaxation"
    ]
    technique = random.choice(techniques)
    
    return f"""
You're a compassionate AI mental health therapist.

User feels {emotion.lower()} ({mood_emoji}) with a sentiment of {sentiment.lower()}, mood score {mood_score}/10.

User says: "{user_input}"

Give an empathetic reply and suggest a mental health tip like "{technique}" with a fact or reasoning.
Keep it friendly and brief.
"""

# -------------------- Chat Interaction --------------------
user_input = st.chat_input("What's on your mind?")

if user_input:
    st.session_state.chat_history.append(("user", user_input))

    with st.spinner("🤖 Thinking..."):
        sentiment = sentiment_model(user_input)[0]["label"]
        emotion = emotion_model(user_input)[0]["label"]
        prompt = build_prompt(user_input, emotion, sentiment, mood_emoji, st.session_state.mood_score)
        response = motivator(prompt, max_length=150, num_return_sequences=1)[0]["generated_text"]

    bot_reply = f"""
🧠 **Emotional Insight**  
You're feeling **{emotion.lower()}** and your sentiment is **{sentiment.lower()}**.

💬 **My Suggestion**  
{response.strip()}
"""

    if st.session_state.mood_score <= 3:
        bot_reply += "\n\n🌬️ *Try this breathing exercise to relax:*"
        bot_reply += "\n![Breathing GIF](https://media.tenor.com/Xk4xzR9U69QAAAAC/breath-in-breath-out.gif)"

    st.session_state.chat_history.append(("bot", bot_reply))

# -------------------- Display Chat --------------------
for sender, msg in reversed(st.session_state.chat_history):
    message(msg, is_user=(sender == "user"), key=f"{sender}_{hash(msg)}")
