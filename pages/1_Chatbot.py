import streamlit as st
from transformers import pipeline
from streamlit_chat import message
import random

st.set_page_config(page_title="SerenityMind Chatbot", page_icon="🧠", layout="wide")
st.markdown("""
    <style>
        body {
            background-color: #fdfdfd;
            color: #333333;
        }
        .stTextInput > div > div > input {
            background-color: #ffffff;
            color: #000000;
        }
        .message-bubble {
            border-radius: 20px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 SerenityMind Chatbot")
st.markdown("<sub>Status: <span style='color:green;'>Online</span></sub>", unsafe_allow_html=True)

@st.cache_resource
def load_models():
    sentiment_model = pipeline("sentiment-analysis")
    emotion_model = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
    motivator = pipeline("text-generation", model="tiiuae/falcon-7b-instruct", trust_remote_code=True)
    return sentiment_model, emotion_model, motivator

sentiment_model, emotion_model, motivator = load_models()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "mood_score" not in st.session_state:
    st.session_state.mood_score = None

user_input = st.text_input("💬 How are you feeling today?", key="input")

if user_input:
    with st.spinner("Analyzing your emotional tone..."):
        sentiment = sentiment_model(user_input)[0]["label"]
        emotion = emotion_model(user_input)[0]["label"]

        if st.session_state.mood_score is None:
            st.markdown("### 🌡️ How would you rate your mood on a scale from 1️⃣ to 🔟?")
            mood_score = st.slider("Mood Score", 1, 10, 5)
            st.session_state.mood_score = mood_score

        prompt = f"You are a compassionate AI therapist. A user says: '{user_input}'. They feel {emotion.lower()} and their sentiment is {sentiment.lower()}, with a mood score of {st.session_state.mood_score}/10. Provide an empathetic response and suggest a psychological technique like gratitude listing or breathing with a real scientific reason."
        motivational_text = motivator(prompt, max_new_tokens=100)[0]["generated_text"]

    st.session_state.chat_history.append(("user", user_input))
    reply = f"""
### 🧠 Emotional Insight
You're feeling **{emotion.lower()}** and your sentiment is **{sentiment.lower()}**.

### 💬 My Suggestion
{motivational_text.strip()}
    """
    st.session_state.chat_history.append(("bot", reply))

st.markdown("---")
st.subheader("💭 Your Conversation")

for sender, msg in reversed(st.session_state.chat_history):
    message(msg, is_user=(sender == "user"), key=f"{sender}_{hash(msg)}")
