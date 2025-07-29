import streamlit as st
from utils.inference_api import query_huggingface_api
from streamlit_lottie import st_lottie
import random

st.set_page_config(page_title="SerenityMind - AI Therapist", page_icon="🧠")

st.markdown("## 🤖 SerenityMind Chatbot")
st.caption("Your mental health companion, always here to talk.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "mood_score" not in st.session_state:
    st.session_state.mood_score = None

st.write("### 🧘 How are you feeling today?")
user_input = st.text_input("Type your thoughts here...")

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    with st.spinner("Analyzing your mood..."):
        sentiment = query_huggingface_api(user_input, "sentiment")
        emotion = query_huggingface_api(user_input, "emotion")
        motivational = query_huggingface_api(f"You feel {emotion[0]['label'].lower()}. Remember,", "motivator")

    mood = emotion[0]['label']
    senti = sentiment[0]['label']
    suggestion = {
        "sadness": "Try gratitude journaling. Listing 3 good things daily boosts happiness.",
        "joy": "Embrace it! Share your joy with someone – happiness grows when shared.",
        "anger": "Take deep breaths. Grounding yourself can lower cortisol.",
        "fear": "Try the 5-4-3-2-1 technique to return to the present moment.",
        "confusion": "Clarity comes with calm. Try box breathing (inhale 4s, hold 4s, exhale 4s)."
    }.get(mood.lower(), "Talking about it helps. Journaling could be a good step.")

    # Mood score UI
    st.write("#### 🌡️ How intense is this feeling? (1-10)")
    mood_score = st.slider("Rate your current mood", 1, 10, 5)
    st.session_state.mood_score = mood_score

    # Chatbot reply
    reply = f"""
**Emotional Insight**

You're feeling **{mood.lower()}** and your sentiment is **{senti.lower()}**.
Mood intensity: **{mood_score}/10**

💬 **My Suggestion**  
{suggestion}

💡 _Here's something uplifting:_  
> {motivational[0]['generated_text'].strip()}
"""
    st.session_state.chat_history.append(("bot", reply))

# Show past chats
for sender, msg in reversed(st.session_state.chat_history):
    with st.chat_message("user" if sender == "user" else "assistant"):
        st.markdown(msg)

st.markdown("---")
st.markdown("Need to relax? Here's a quick **breathing animation**:")
st.image("assets/breathing.gif", use_column_width=True)
