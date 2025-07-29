import streamlit as st
from transformers import pipeline
from streamlit_chat import message

st.set_page_config(page_title="Chatbot - SerenityMind")
st.title("🧠 SerenityMind Chatbot")

@st.cache_resource
def load_models():
    sentiment_model = pipeline("sentiment-analysis")
    emotion_model = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
    motivator = pipeline("text-generation", model="mrm8488/GPT-2-finetuned-positive-motivational")
    return sentiment_model, emotion_model, motivator

sentiment_model, emotion_model, motivator = load_models()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("How are you feeling today?", key="input")

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    with st.spinner("Analyzing..."):
        sentiment = sentiment_model(user_input)[0]["label"]
        emotion = emotion_model(user_input)[0]["label"]
        motivational_text = motivator(f"You feel {emotion.lower()}. Remember,", max_length=50)[0]["generated_text"]

    reply = f"""
I sense you're feeling **{emotion.lower()}** and your sentiment is **{sentiment.lower()}**.
🌟 Here's something to lift you up:
> _{motivational_text.strip()}_
"""
    st.session_state.chat_history.append(("bot", reply))

for sender, msg in reversed(st.session_state.chat_history):
    message(msg, is_user=(sender == "user"), key=f"{sender}_{hash(msg)}")
