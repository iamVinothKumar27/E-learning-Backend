from flask import Flask, render_template_string, request
import os
import json
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

app = Flask(__name__)

# Load environment variables
load_dotenv()

GOOGLE_API_KEY = "AIzaSyA1-425hbFs_LxQmwDvXADI3wL_3yqlJkQ"
if not GOOGLE_API_KEY:
    print("GOOGLE_API_KEY not found. Please make sure it is set in the .env file.")
    exit(1)

# Initialize the Chat model using gemini-2.0-flash
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.5, google_api_key=GOOGLE_API_KEY)

# Read the video transcript details from the JSON file
file_path = "C:/Users/gokul/HackFest/gps/src/backend/video_details/video_details_Web Development.json"
try:
    with open(file_path, "r", encoding="utf-8") as file:
        video_details = json.load(file)  # Properly load JSON data
except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
    exit(1)
except json.JSONDecodeError:
    print(f"Error: Failed to decode JSON from {file_path}")
    exit(1)

# Combine transcripts from all videos
combined_transcript = "\n".join(item.get("transcript", "") for item in video_details)

# Define a prompt template for generating a quiz
prompt_template = """
You are an expert quiz generator. Based on the transcript provided below about Artificial Intelligence,
generate a list of 10 multiple-choice questions in **valid JSON format**. The output should be a JSON object **with only the following structure**:

{{
    "questions": [
        {{
            "id": 1,
            "text": "What is AI?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct": "Option A"
        }},
        ...
    ]
}}

Strictly return **only** the JSON object and nothing else. Do not include any introductory or explanatory text.
Transcript:
{transcript}
"""


formatted_prompt = prompt_template.format(transcript=combined_transcript)

# Invoke the model to generate the quiz
quiz_response = model.invoke(formatted_prompt)

# Extract the response content
quiz_text = quiz_response.content if hasattr(quiz_response, "content") else str(quiz_response)

# Ensure the response is valid JSON
match = re.search(r'\{.*\}', quiz_text, re.DOTALL)
if match:
    try:
        questions = json.loads(match.group())["questions"]
    except json.JSONDecodeError:
        print("Error: Extracted content is not valid JSON.")
        exit(1)
else:
    print("Error: No JSON detected in the AI response.")
    exit(1)

# HTML Template
template = """
<!DOCTYPE html>
<html>
<head>
    <title> Quiz</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .question { margin-bottom: 20px; padding: 15px; border: 1px solid #ccc; border-radius: 5px; }
        .options { margin-top: 10px; }
        .check-answer { margin-top: 10px; }
        .correct { color: green; font-weight: bold; }
        .incorrect { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Quiz</h1>
    <form method="POST">
        {% for question in questions %}
            <div class="question">
                <p><strong>{{ loop.index }}. {{ question.text }}</strong></p>
                <div class="options">
                    {% for option in question.options %}
                        <label>
                            <input type="radio" name="q{{ question.id }}" value="{{ option }}">
                            {{ option }}
                        </label><br>
                    {% endfor %}
                </div>
            </div>
        {% endfor %}
        <button type="submit">Submit</button>
    </form>

    {% if feedback %}
        <div style="margin-top: 20px;">
            <h3>Results:</h3>
            {% for fb in feedback %}
                <p class="{{ 'correct' if fb.is_correct else 'incorrect' }}">
                    <strong>Question {{ fb.question_id }}:</strong> {{ fb.message }}
                </p>
            {% endfor %}
        </div>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def quiz():
    feedback = []
    c=0
    if request.method == 'POST':
        for question in questions:
            question_id = str(question["id"])
            user_answer = request.form.get(f'q{question_id}')
            
            if user_answer:
                is_correct = user_answer == question["correct"]
                feedback.append({
                    "question_id": question_id,
                    "message": f"Your answer is {'correct' if is_correct else f'incorrect'}",
                    "is_correct": is_correct
                })
    
    return render_template_string(template, questions=questions, feedback=feedback)

if __name__ == '__main__':
    app.run(debug=True,port=5050)
