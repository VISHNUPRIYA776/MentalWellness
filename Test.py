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

# Function to check if the username exists
def student_exists(username):
    conn = sqlite3.connect('student_mood_tracker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM students WHERE username = ?', (username,))
    student = c.fetchone()
    conn.close()
    return student is not None

# Function to create a new student
def create_student(username, password, preferred_times, major):
    if student_exists(username):
        return False  # Username already exists
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect('student_mood_tracker.db')
    c = conn.cursor()
    c.execute('INSERT INTO students (username, password, preferred_times, major) VALUES (?, ?, ?, ?)', 
              (username, hashed_pw, preferred_times, major))
    conn.commit()
    conn.close()
    return True

# Function to authenticate a student
def authenticate_student(username, password):
    conn = sqlite3.connect('student_mood_tracker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM students WHERE username = ?', (username,))
    student = c.fetchone()
    conn.close()
    if student and bcrypt.checkpw(password.encode('utf-8'), student[2].encode('utf-8')):
        return student
    return None

# Function to check if current time is within the student's preferred times
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

# Function to analyze mood (dummy function for now)
def analyze_sentiment(text):
    sentiments = ["Positive", "Neutral", "Negative"]
    sentiment = random.choice(sentiments)
    score = round(random.uniform(0.5, 1.0), 2)
    return sentiment, score

# Function to get a recommendation based on sentiment and study stress
def get_recommendation(sentiment, score, major):
    if sentiment == "Positive":
        return {
            "message": "Keep up the great work! Stay positive and share your happiness with others.",
            "study_tip": "Take 5-minute breaks after every 45 minutes of studying. Your mind works best with short breaks.",
            "stress_management": "Try mindfulness meditation or deep-breathing exercises to reduce stress.",
            "academic_resource": f"Check out 'The Study Skills Handbook' for tips related to your {major} major."
        }
    elif sentiment == "Neutral":
        return {
            "message": "It's okay to feel neutral. Take things slow and focus on balancing studies with self-care.",
            "study_tip": "Try breaking larger tasks into smaller, manageable chunks to reduce overwhelm.",
            "stress_management": "Engage in some light physical activity like a short walk or stretching.",
            "academic_resource": f"Visit your department's office hours to get help on assignments related to {major}."
        }
    else:
        return {
            "message": "It's okay to have off days. Focus on your well-being and talk to someone if needed.",
            "study_tip": "Prioritize sleep! Lack of sleep affects concentration and stress levels.",
            "stress_management": "Try journaling your thoughts or seek support from campus counseling.",
            "academic_resource": f"Look into academic counseling services for help with managing stress in your {major} coursework."
        }

# Function to insert mood data into the database
def insert_mood_entry(student_id, date, mood_text, sentiment, sentiment_score, recommendation):
    conn = sqlite3.connect('student_mood_tracker.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO mood_entries (student_id, date, mood_text, sentiment, sentiment_score, recommendation)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (student_id, date, mood_text, sentiment, sentiment_score, recommendation["message"]))
    conn.commit()
    conn.close()

# Function to get mood history for a student
def get_mood_history(student_id):
    conn = sqlite3.connect('student_mood_tracker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM mood_entries WHERE student_id = ?', (student_id,))
    data = c.fetchall()
    conn.close()
    return data

# Function to add study goals
def add_study_goal(student_id, goal):
    conn = sqlite3.connect('student_mood_tracker.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO study_goals (student_id, goal, created_at) 
        VALUES (?, ?, ?)
    ''', (student_id, goal, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# Function to get study goals
def get_study_goals(student_id):
    conn = sqlite3.connect('student_mood_tracker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM study_goals WHERE student_id = ?', (student_id,))
    data = c.fetchall()
    conn.close()
    return data

# Function to update study goal status
def update_study_goal_status(goal_id, status):
    conn = sqlite3.connect('student_mood_tracker.db')
    c = conn.cursor()
    c.execute('UPDATE study_goals SET status = ? WHERE id = ?', (status, goal_id))
    conn.commit()
    conn.close()

# Function to visualize mood trends
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

# Main Streamlit app
def main():
    st.set_page_config(page_title="📚 Student Mental Wellness App", layout="wide")
    st.markdown("<h1 style='text-align: center; color: #4e73df;'>📚 Student Mental Wellness App</h1>", unsafe_allow_html=True)

    # Initialize the database
    init_db()

    if "student_id" not in st.session_state:
        st.session_state.student_id = None

    # User login/signup selection
    option = st.sidebar.radio("Select Action", ["Login", "Sign Up"])

    if option == "Login":
        st.sidebar.header("🔒 Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Submit"):
            student = authenticate_student(username, password)
            if student:
                student_id, _, _, preferred_times, major = student
                if is_within_preferred_times(preferred_times):
                    st.sidebar.success("Logged in successfully!")
                    st.session_state.student_id = student_id
                else:
                    st.sidebar.error(f"App can only be accessed during your preferred time: {preferred_times}.")
            else:
                st.sidebar.error("Invalid username or password.")

    elif option == "Sign Up":
        st.sidebar.header("📜 Sign Up")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        preferred_times = st.sidebar.selectbox("Preferred Times", ["Morning", "Afternoon", "Evening", "Night"])
        major = st.sidebar.text_input("Your Major")
        if st.sidebar.button("Create Account"):
            if create_student(username, password, preferred_times, major):
                st.sidebar.success("Account created successfully! Please log in.")
            else:
                st.sidebar.error("Username already exists! Please choose a different username.")

    # If logged in, show the app content
    if st.session_state.student_id:
        st.markdown("### 🌤️ View Your Mood History and Resources")
        history_button = st.button("View Mood History")
        if history_button:
            mood_history = get_mood_history(st.session_state.student_id)
            if mood_history:
                df = pd.DataFrame(mood_history, columns=["ID", "Student ID", "Date", "Mood", "Sentiment", "Sentiment Score", "Recommendation"])
                st.write(df)
                plot_mood_trends(mood_history)
            else:
                st.write("No mood history found.")

        st.markdown("### 🌤️ Analyze Your Mood (Available only during your preferred time)")
        mood_text = st.text_area("Enter your thoughts or feelings:")
        if st.button("Analyze Mood") and mood_text:
            student = authenticate_student(username, password)
            if student:
                preferred_times = student[3]  # Retrieve student's preferred time slot
                major = student[4]  # Retrieve student's major
                if is_within_preferred_times(preferred_times):
                    sentiment, score = analyze_sentiment(mood_text)
                    recommendation = get_recommendation(sentiment, score, major)
                    insert_mood_entry(st.session_state.student_id, datetime.now(), mood_text, sentiment, score, recommendation)
                    st.success(f"**Sentiment:** {sentiment} | **Score:** {score}")
                    st.write(f"**Recommendation:** {recommendation['message']}")
                    st.write(f"**Study Tip:** {recommendation['study_tip']}")
                    st.write(f"**Stress Management Tip:** {recommendation['stress_management']}")
                    st.write(f"**Academic Resource:** {recommendation['academic_resource']}")
                else:
                    st.error(f"Mood analysis is available only during your preferred time: {preferred_times}.")
            
        st.markdown("### 📚 Set Your Study Goals")
        study_goal = st.text_input("Enter your study goal:")
        if st.button("Set Goal") and study_goal:
            add_study_goal(st.session_state.student_id, study_goal)
            st.success(f"Study goal '{study_goal}' set successfully!")

        st.markdown("### 🎯 View and Update Your Study Goals")
        goals = get_study_goals(st.session_state.student_id)
        if goals:
            goal_df = pd.DataFrame(goals, columns=["ID", "Student ID", "Goal", "Status", "Created At"])
            st.write(goal_df)
            for index, goal in goal_df.iterrows():
                if st.button(f"Complete Goal {goal['ID']}"):
                    update_study_goal_status(goal['ID'], "Completed")
                    st.success(f"Goal {goal['ID']} marked as completed!")
        else:
            st.write("No study goals found.")
