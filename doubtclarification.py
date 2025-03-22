import google.generativeai as genai
from flask import Flask, request, jsonify, render_template_string
import json
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Define the JSON file containing the transcript
TRANSCRIPT_FILE = "C:/Users/gokul/HackFest/gps/src/backend/video_details/video_details_Web Development.json"

# Function to load transcript from JSON file
def load_transcript():
    if os.path.exists(TRANSCRIPT_FILE):
        with open(TRANSCRIPT_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("transcript", "")  # Extract transcript from the first object
    return ""  # Return empty string if file doesn't exist or has incorrect format

# Load the transcript
TRANSCRIPT = load_transcript()

# Initialize Flask app
app = Flask(__name__)

# Initialize Gemini Pro API
genai.configure(api_key="AIzaSyCLaBBXT4IIOxcr0vtD7ZB21f9qqcHW64E")  # Replace with your API key

# In-memory storage for conversations
conversations = []

# HTML Template for UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Doubt Clearing Bot</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center text-primary">AI Doubt Clearing Bot</h1>
        
        <!-- Clear All Button -->
        <form method="POST" action="/clear_all">
            <button type="submit" class="btn btn-danger mb-3">Clear All Conversations</button>
        </form>
        
        <!-- Question Form -->
        <form method="POST" action="/ask">
            <div class="mb-3">
                <label for="question" class="form-label">Enter your Question</label>
                <input type="text" id="question" name="question" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-primary">Ask</button>
        </form>

        <!-- Display Conversations -->
        {% if conversations %}
        <div class="mt-4">
            <h3>Past Conversations:</h3>
            <ul class="list-group">
                {% for question, answer in conversations %}
                    <li class="list-group-item">
                        <strong>Q:</strong> {{ question }}<br>
                        <strong>A:</strong> {{ answer }}
                    </li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

# Function to check if the question is semantically related to the transcript
def is_related_to_transcript(question):
    if not TRANSCRIPT:
        return False  # No transcript available

    vectorizer = CountVectorizer().fit_transform([TRANSCRIPT, question])
    cosine_sim = cosine_similarity(vectorizer[0:1], vectorizer[1:2])

    return cosine_sim[0][0] > 0.2  # Threshold for relevance

# Function to check if the question is within the scope of the transcript
def is_within_scope(question):
    if not TRANSCRIPT:
        return False  # No transcript available

    prompt = f"Check if the question is within the scope of the following transcript:\n\n{TRANSCRIPT}\n\nQuestion: {question}\nAnswer with 'Yes' or 'No'."
    response = genai.GenerativeModel('gemini-2.0-flash').generate_content(prompt)
    
    return response.text.strip().lower() == 'yes'

# Function to answer the question based on the transcript
def get_answer_from_transcript(question):
    if not TRANSCRIPT:
        return "No transcript available to answer the question."

    prompt = f"Answer the following question based on this transcript:\n\n{TRANSCRIPT}\n\nQuestion: {question}\nAnswer concisely."
    response = genai.GenerativeModel('gemini-2.0-flash').generate_content(prompt)
    
    return response.text.strip()

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_TEMPLATE, conversations=conversations)

@app.route("/ask", methods=["POST"])
def ask():
    question = request.form["question"]
    
    if is_within_scope(question):
        answer = get_answer_from_transcript(question)
    elif is_related_to_transcript(question):
        answer = "Your question is related to the transcript, but it is not explicitly present in the content. Can you please clarify?"
    else:
        answer = "Your question doesn't lie within the covered concepts."
    
    # Store the conversation
    conversations.append((question, answer))
    
    return render_template_string(HTML_TEMPLATE, conversations=conversations)

@app.route("/clear_all", methods=["POST"])
def clear_all():
    conversations.clear()
    return render_template_string(HTML_TEMPLATE, conversations=conversations)

if __name__ == "__main__":
    app.run(debug=True, port=8000)
