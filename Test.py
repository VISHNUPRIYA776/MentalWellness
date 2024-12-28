import streamlit as st
import sqlite3
from datetime import datetime, time
import random
import bcrypt
import pandas as pd
import matplotlib.pyplot as plt

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('student_mood_tracker.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            preferred_times TEXT,
            major TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS mood_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date TEXT,
            mood_text TEXT,
            sentiment TEXT,
            sentiment_score REAL,
            recommendation TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS study_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            goal TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    ''')
    conn.commit()
    conn.close()

# Helper functions
def student_exists(username):
    conn = sqlite3.connect('student_mood_tracker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM students WHERE username = ?', (username,))
    student = c.fetchone()
    conn.close()
    return student is not None

def create_student(username, password, preferred_times, major):
    if student_exists(username):
        return False
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect('student_mood_tracker.db')
    c = conn.cursor()
    c.execute('INSERT INTO students (username, password, preferred_times, major) VALUES (?, ?, ?, ?)', 
              (username, hashed_pw, preferred_times, major))
    conn.commit()
    conn.close()
    return True

def authenticate_student(username, password):
    conn = sqlite3.connect('student_mood_tracker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM students WHERE username = ?', (username,))
    student = c.fetchone()
    conn.close()
    if student and bcrypt.checkpw(password.encode('utf-8'), student[2].encode('utf-8')):
        return student
    return None

def is_within_preferred_times(preferred_times):
    time_ranges = {
        "Morning": (time(6, 0), time(12, 0)),
        "Afternoon": (time(12, 0), time(17, 0)),
        "Evening": (time(17, 0), time(20, 0)),
        "Night": (time(20, 0), time(23, 59))
    }
    current_time = datetime.now().time()
    start, end = time_ranges.get(preferred_times, (time(0, 0), time(23, 59)))
    return start <= current_time <= end

def analyze_sentiment(text):
    sentiments = ["Positive", "Neutral", "Negative"]
    sentiment = random.choice(sentiments)
    score = round(random.uniform(0.5, 1.0), 2)
    return sentiment, score

def get_recommendation(sentiment, score, major):
    if sentiment == "Positive":
        return f"Stay positive! Focus on your goals and keep improving in your {major} major."
    elif sentiment == "Neutral":
        return f"Take things slow. Reflect on what motivates you in your {major} studies."
    else:
        return f"Take care of your mental health. Seek support if your {major} coursework feels overwhelming."

def insert_mood_entry(student_id, date, mood_text, sentiment, sentiment_score, recommendation):
    conn = sqlite3.connect('student_mood_tracker.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO mood_entries (student_id, date, mood_text, sentiment, sentiment_score, recommendation)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (student_id, date, mood_text, sentiment, sentiment_score, recommendation))
    conn.commit()
    conn.close()

def get_mood_history(student_id):
    conn = sqlite3.connect('student_mood_tracker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM mood_entries WHERE student_id = ?', (student_id,))
    data = c.fetchall()
    conn.close()
    return data

def add_study_goal(student_id, goal):
    conn = sqlite3.connect('student_mood_tracker.db')
    c = conn.cursor()
    c.execute('INSERT INTO study_goals (student_id, goal, created_at) VALUES (?, ?, ?)', 
              (student_id, goal, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_study_goals(student_id):
    conn = sqlite3.connect('student_mood_tracker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM study_goals WHERE student_id = ?', (student_id,))
    data = c.fetchall()
    conn.close()
    return data

def update_study_goal_status(goal_id, status):
    conn = sqlite3.connect('student_mood_tracker.db')
    c = conn.cursor()
    c.execute('UPDATE study_goals SET status = ? WHERE id = ?', (status, goal_id))
    conn.commit()
    conn.close()

def plot_mood_trends(mood_history):
    sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
    for entry in mood_history:
        sentiment_counts[entry[4]] += 1

    labels = sentiment_counts.keys()
    sizes = sentiment_counts.values()

    plt.figure(figsize=(6, 4))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.title("Mood Sentiment Distribution")
    st.pyplot(plt)

# Main App
def main():
    st.set_page_config(page_title="Student Mental Wellness", layout="wide")
    st.title("📚 Student Mental Wellness App")

    init_db()

    if "student_id" not in st.session_state:
        st.session_state.student_id = None

    option = st.sidebar.radio("Choose Action", ["Login", "Sign Up"])

    if option == "Login":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            student = authenticate_student(username, password)
            if student:
                st.session_state.student_id, _, _, preferred_times, major = student
                st.success(f"Welcome back, {username}!")
            else:
                st.error("Invalid credentials.")

    elif option == "Sign Up":
        username = st.sidebar.text_input("Create Username")
        password = st.sidebar.text_input("Create Password", type="password")
        preferred_times = st.sidebar.selectbox("Preferred Times", ["Morning", "Afternoon", "Evening", "Night"])
        major = st.sidebar.text_input("Your Major")
        if st.sidebar.button("Sign Up"):
            if create_student(username, password, preferred_times, major):
                st.success("Account created! Please log in.")
            else:
                st.error("Username already exists.")

    if st.session_state.student_id:
        tab1, tab2, tab3 = st.tabs(["🎭 Mood Tracker", "🎯 Study Goals", "📊 Trends"])

        with tab1:
            mood_text = st.text_area("How are you feeling today?")
            if st.button("Analyze Mood"):
                sentiment, score = analyze_sentiment(mood_text)
                recommendation = get_recommendation(sentiment, score, "General")
                insert_mood_entry(st.session_state.student_id, datetime.now().isoformat(), mood_text, sentiment, score, recommendation)
                st.success(f"Sentiment: {sentiment} (Score: {score})")
                st.write(f"Recommendation: {recommendation}")

        with tab2:
            goal = st.text_input("Set a Study Goal:")
            if st.button("Add Goal"):
                add_study_goal(st.session_state.student_id, goal)
                st.success(f"Goal '{goal}' added!")

            goals = get_study_goals(st.session_state.student_id)
            if goals:
                for g in goals:
                    st.write(f"Goal: {g[2]} | Status: {g[3]}")
                    if g[3] == "Pending" and st.button(f"Mark Goal {g[0]} Completed"):
                        update_study_goal_status(g[0], "Completed")
                        st.success(f"Goal {g[0]} completed!")

        with tab3:
            mood_history = get_mood_history(st.session_state.student_id)
            if mood_history:
                plot_mood_trends(mood_history)
            else:
                st.write("No mood history found.")

if __name__ == "__main__":
    main()
