import os
import sqlite3
from flask import Flask, request, jsonify, render_template
import random
from groq import Groq
from flask_cors import CORS

app = Flask(__name__)
# Allow all origins for development
CORS(app, resources={r"/*": {"origins": "*"}})

# SQLite setup (for user management)
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

# Groq client initialization
groq_client = Groq(api_key="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")

# Bio generation function using Groq API
def generate_bio(career, personality, interest, relationship_goal, name, template, emoji, social_links):
    try:
        # Format the query for generating a personalized bio
        query = (
            f"Generate a personalized bio for a user based on the following details: "
            f"Career: {career}, Personality: {personality}, Interests: {interest}, "
            f"Relationship goal: {relationship_goal}. "
            "The bio should be engaging, relevant, and reflect the user's preferences. "
            "Make it suitable for use on social platforms or introductions."
        )
        
        # Call the Groq API
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": query}],
            model="llama3-8b-8192",
            stream=False,
        )
        
        # Extract the bio from the response
        bio = chat_completion.choices[0].message.content.strip()
        
        # Apply the selected template (short/detailed)
        if template == "short":
            bio = bio.split('.')[0]  # Get the first sentence for short bio
        
        # Add emojis or social links if selected
        if emoji:
            bio += " 🎉"
        if social_links:
            bio += f"\nFollow {name} on Instagram: [@username](https://instagram.com/username)"
        
        return bio
    except Exception as e:
        return f"Error generating bio: {str(e)}"


# Route to render the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to generate bio based on form inputs
@app.route('/generate_bio', methods=['POST'])
def generate_bio_route():
    try:
        data = request.form
        bio = generate_bio(
            data['career'],
            data['personality'],
            data['interest'],
            data['relationship_goal'],
            data['name'],
            data['template'],
            'emoji' in data,
            'social_links' in data
        )
        return jsonify({'bio': bio})
    except KeyError as e:
        return jsonify({'error': f"Missing field: {str(e)}"}), 400

# Route for user signup
@app.route('/signup', methods=['POST'])
def signup():
    data = request.form
    create_user(data['email'], data['password'])
    return jsonify({'message': 'Signup successful!'})

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.form
    user = authenticate_user(data['email'], data['password'])
    if user:
        return jsonify({'message': 'Login successful!'})
    else:
        return jsonify({'message': 'Invalid credentials'}), 400

# Route to handle rating
@app.route('/rate_bio', methods=['POST'])
def rate_bio():
    data = request.get_json()
    rating = data.get('rating')
    if rating is None:
        return jsonify({'error': 'Rating is required'}), 400
    return jsonify({'message': 'Rating received'})

# Route for random bio suggestion
@app.route('/random_bio', methods=['GET'])
def random_bio_route():
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
    return jsonify({'bio': random_bio})

if __name__ == '__main__':
    app.run(debug=True)