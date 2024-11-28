import os
import streamlit as st
import random
import sqlite3
import requests
import json

def query_groq_api(text, concise=False):
    api_key = st.secrets["GROQ_API_KEY"]
    endpoint = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "messages": [
           
            {
                "role": "user",
                "content": text
            }
        ],
        "model": "llama3-8b-8192"
    }

    try:
        response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"Error querying Groq API: {str(e)}")
        return None

def create_user(email, password):
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT, password TEXT)')
        c.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
        conn.commit()

def authenticate_user(email, password):
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email=? AND password=?', (email, password))
        return c.fetchone()

def generate_bio(career, personality, interest, relationship_goal, name, template, emoji, social_links):
    try:
        query = (
            f"Generate a personalized bio for a user based on the following details: "
            f"Career: {career}, Personality: {personality}, Interests: {interest}, "
            f"Relationship goal: {relationship_goal}. "
            "The bio should be engaging, relevant, and reflect the user's preferences. "
            "Make it suitable for use on social platforms or introductions."
        )

        bio = query_groq_api(query)

        if template == "short":
            bio = bio.split('.')[0]  # Get the first sentence for short bio

        if emoji:
            bio += " 🎉"
        if social_links:
            bio += f"\nFollow {name} on Instagram: [@username](https://instagram.com/username)"

        return bio
    except Exception as e:
        return f"Error generating bio: {str(e)}"

def main():
    st.set_page_config(page_title="DinnerTonight Bio Generator", page_icon="🍽️")
    
    st.title("DinnerTonight Bio Generator")

    # Sidebar for navigation
    menu = ["Bio Generator", "Login", "Signup"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Bio Generator":
        st.header("Generate Your Perfect Bio")

        # Collect user inputs
        name = st.text_input("Enter Your Name", key="name")
        
        col1, col2 = st.columns(2)
        
        with col1:
            career = st.selectbox("Select Career", 
                ["Software Engineer", "Artist", "Chef", "Teacher", "Musician"])
            
            personality = st.selectbox("Select Personality", 
                ["Adventurous", "Creative", "Compassionate", "Introverted"])
        
        with col2:
            interest = st.selectbox("Select Interest", 
                ["Cooking", "Traveling", "Music", "Literature", "Gaming"])
            
            relationship_goal = st.selectbox("Select Relationship Goal", 
                ["Casual", "Long-term", "Adventurous"])

        template = st.radio("Bio Template", ["short", "detailed"])
        
        col3, col4 = st.columns(2)
        
        with col3:
            emoji = st.checkbox("Include Emoji")
        
        with col4:
            social_links = st.checkbox("Include Social Links")

        if st.button("Generate Bio"):
            if name:
                bio = generate_bio(career, personality, interest, 
                                   relationship_goal, name, template, emoji, social_links)
                st.success("Bio Generated!")
                st.write(bio)
            else:
                st.warning("Please enter your name!")

        # Random Bio Generation
        if st.button("Get Random Bio"):
            careers = ['Software Engineer', 'Artist', 'Chef', 'Teacher', 'Musician']
            personalities = ['Adventurous', 'Creative', 'Compassionate', 'Introverted']
            interests = ['Cooking', 'Traveling', 'Music', 'Literature', 'Gaming']
            relationship_goals = ['Casual', 'Long-term', 'Adventurous']

            random_bio = generate_bio(
                random.choice(careers),
                random.choice(personalities),
                random.choice(interests),
                random.choice(relationship_goals),
                'User',
                'short',
                emoji=False,
                social_links=False
            )
            st.success("Random Bio Generated!")
            st.write(random_bio)

    elif choice == "Login":
        st.header("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            user = authenticate_user(email, password)
            if user:
                st.success("Login Successful!")
            else:
                st.error("Invalid Credentials")

    elif choice == "Signup":
        st.header("Create an Account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Signup"):
            if password == confirm_password:
                create_user(email, password)
                st.success("Account Created Successfully!")
            else:
                st.error("Passwords Do Not Match")

if __name__ == "__main__":
    main()