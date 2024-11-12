import streamlit as st
import speech_recognition as sr
from transformers import pipeline
from datetime import datetime
import pandas as pd
import sqlite3
import random

# Initialize the sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

# SQLite Database setup
def init_db():
    conn = sqlite3.connect('mood_tracker.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS mood_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            text TEXT,
            sentiment TEXT,
            score REAL,
            recommendation TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Insert mood entry into the database
def insert_mood_entry(date, text, sentiment, score, recommendation):
    conn = sqlite3.connect('mood_tracker.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO mood_history (date, text, sentiment, score, recommendation) 
        VALUES (?, ?, ?, ?, ?)
    ''', (date, text, sentiment, score, recommendation))
    conn.commit()
    conn.close()

# Retrieve mood history from the database
def get_mood_history():
    conn = sqlite3.connect('mood_tracker.db')
    c = conn.cursor()
    c.execute('SELECT date, text, sentiment, score, recommendation FROM mood_history')
    data = c.fetchall()
    conn.close()
    return data

# Initialize the database
init_db()

# Function for speech-to-text conversion
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening for your input...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            st.write("**You said:**", text)
            return text
        except sr.UnknownValueError:
            st.error("❌ Sorry, I couldn't understand.")
            return None
        except sr.RequestError:
            st.error("❌ There was an error with the speech recognition service.")
            return None

# Function to analyze sentiment of the text
def analyze_sentiment(text):
    result = sentiment_analyzer(text)[0]
    sentiment = result['label']
    score = result['score']
    return sentiment, score

# Function for generating recommendations based on sentiment
def get_recommendation(sentiment, score):
    if sentiment == "POSITIVE":
        if score > 0.7:
            return "🌟 You're feeling positive! Keep this momentum by doing something productive."
        else:
            return "😊 You seem in a good mood. Take a short walk or do a fun hobby!"
    elif sentiment == "NEGATIVE":
        if score > 0.7:
            return "😓 Feeling stressed? Try a break—stretch, breathe, or chat with a friend."
        else:
            return "😔 A bit down? Try a relaxation exercise or something enjoyable."
    else:
        return "💭 Self-care can help. Try journaling or a quick mindfulness exercise."

# Function for mood-based motivational quotes
def get_motivational_quote(sentiment):
    positive_quotes = [
        "Keep going! You're doing great.",
        "Believe in yourself, you are capable of amazing things!",
        "Embrace the journey, you’re on the right path."
    ]
    negative_quotes = [
        "Every day may not be good, but there is something good in every day.",
        "Don’t be discouraged by challenges; they make you stronger.",
        "Take a deep breath, and take things one step at a time."
    ]
    if sentiment == "POSITIVE":
        return random.choice(positive_quotes)
    else:
        return random.choice(negative_quotes)

# Function to suggest mood-based music
def get_music_suggestion(sentiment):
    if sentiment == "POSITIVE":
        return "🎶 How about some upbeat music to keep your spirits high?"
    elif sentiment == "NEGATIVE":
        return "🎶 Try listening to calming instrumental music to relax."
    else:
        return "🎶 Music can lift your mood. Choose something you enjoy!"

# Guided breathing exercise
def guided_breathing_exercise():
    st.markdown("""
    **🌬️ Guided Breathing Exercise:**
    - **Inhale** slowly through your nose for **4 seconds**
    - **Hold** your breath for **4 seconds**
    - **Exhale** through your mouth for **4 seconds**
    """)
    st.write("Repeat this exercise a few times to calm your mind.")

# Main Streamlit app
def main():
    st.set_page_config(page_title="🌈 Mental Well-being App", layout="wide")
    st.markdown("<h1 style='text-align: center; color: #4e73df;'>🌈 Mental Well-being App for Students</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6c757d;'>Analyze your mood and receive personalized recommendations.</p>", unsafe_allow_html=True)

    # Suggested Times
    st.markdown("<h3 style='color: #ff6f61;'>⏰ Suggested Times to Use the App:</h3>", unsafe_allow_html=True)
    st.write("""
    - **Morning:** Set a positive tone for your day.
    - **Afternoon:** Midday check-in to manage stress.
    - **Evening:** Reflect on your day's achievements.
    - **Night:** Calm your mind for restful sleep.
    """)

    # Tabs for easy navigation
    tabs = st.tabs(["Mood Analysis", "Mood Tracker", "Recommendation History", "Resources"])

    # Mood Analysis Tab
    with tabs[0]:
        st.markdown("<h2 style='color: #28a745;'>🧘 Analyze Your Mood</h2>", unsafe_allow_html=True)
        user_text = st.text_input("💬 Type your thoughts here:")

        # Speech input
        if st.button("🎙️ Speak"):
            user_text = speech_to_text()

        # Submit for analysis
        if st.button("🧩 Analyze Mood") and user_text:
            sentiment, score = analyze_sentiment(user_text)
            recommendation = get_recommendation(sentiment, score)
            motivational_quote = get_motivational_quote(sentiment)
            music_suggestion = get_music_suggestion(sentiment)

            st.success(f"**Sentiment Analysis Result:** {sentiment} (Confidence: {score:.2f})")
            st.write(f"**📝 Recommendation:** {recommendation}")
            st.write(f"**💬 Motivational Quote:** {motivational_quote}")
            st.write(f"**🎵 Music Suggestion:** {music_suggestion}")

            # Save to SQLite database
            insert_mood_entry(datetime.now(), user_text, sentiment, score, recommendation)
            st.success("Your mood entry and recommendation have been saved.")

    # Mood Tracker Tab
    with tabs[1]:
        st.markdown("<h2 style='color: #17a2b8;'>📊 Mood Tracker</h2>", unsafe_allow_html=True)
        history_data = get_mood_history()
        if history_data:
            history_df = pd.DataFrame(history_data, columns=["Date", "Text", "Sentiment", "Score", "Recommendation"])
            st.line_chart(history_df[['Date', 'Score']].set_index('Date'))
        else:
            st.info("No mood data available yet.")

    # Recommendation History Tab
    with tabs[2]:
        st.markdown("<h2 style='color: #fd7e14;'>📝 Recommendation History</h2>", unsafe_allow_html=True)
        if history_data:
            history_df = pd.DataFrame(history_data, columns=["Date", "Text", "Sentiment", "Score", "Recommendation"])
            st.table(history_df[["Date", "Text", "Sentiment", "Recommendation"]])
        else:
            st.info("No recommendations yet.")

    # Resources Tab
    with tabs[3]:
        st.markdown("<h2 style='color: #6610f2;'>🌐 Resources</h2>", unsafe_allow_html=True)
        st.write("Find helpful resources for mental well-being:")
        st.markdown("- [Mental Health Foundation](https://www.mentalhealth.org.uk/)")
        st.markdown("- [Mindfulness Exercises](https://www.mindful.org/)")
        st.markdown("- [Mental Health Hotline](https://www.mentalhealth.gov/get-help/immediate-help)")

        # Guided Breathing
        if st.button("🌬️ Try a Breathing Exercise"):
            guided_breathing_exercise()

if __name__ == "__main__":
    main()
