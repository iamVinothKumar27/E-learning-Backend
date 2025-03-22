from flask import Flask, jsonify, render_template_string, request, send_file
import google.generativeai as genai
import json
import os

# Set API Key (Replace with your actual key)
API_KEY = "AIzaSyBvxyDsdmx58DWtzJOgaygRWdqwSKsYGBs"

# Configure Google Generative AI with API key
genai.configure(api_key=API_KEY)

# Initialize Gemini model (using gemini-2.0-flash for speed)
model = genai.GenerativeModel("gemini-2.0-flash")

# Flask app setup
app = Flask(__name__)

# Absolute path for summary storage
SUMMARY_DIR = os.path.abspath("summaries")
os.makedirs(SUMMARY_DIR, exist_ok=True)

# Function to read JSON file
def read_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        return {"error": f"Failed to read JSON file: {str(e)}"}

# Function to summarize content using Gemini AI
def summarize_content(content):
    prompt = f"Summarize the following transcript into key points:\n\n{content}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response else "Summarization failed."
    except Exception as e:
        return f"Error in summarization: {str(e)}"

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_TEMPLATE, summary=None, filename=None)

@app.route("/summarize", methods=["POST"])
def summarize_json():
    json_data = read_json("C:/Users/gokul/HackFest/gps/src/backend/video_details/video_details_Web Development.json")

    if "error" in json_data:
        return jsonify({"error": json_data["error"]}), 500

    transcript_text = " ".join(item.get("transcript", "") for item in json_data if "transcript" in item)
    
    if not transcript_text.strip():
        return jsonify({"error": "No transcript content found in JSON"}), 400

    summary = summarize_content(transcript_text)

    summary_filename = os.path.join(SUMMARY_DIR, "summary.txt")
    with open(summary_filename, "w", encoding="utf-8") as file:
        file.write(summary)

    return render_template_string(HTML_TEMPLATE, summary=summary, filename="summary.txt")

@app.route("/download/<filename>")
def download_summary(filename):
    file_path = os.path.join(SUMMARY_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_file(file_path, as_attachment=True)

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Summarizer</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css">
</head>
<body class="bg-light">
    <div class="container mt-5">
        <h1 class="text-center text-primary">Video Summarizer</h1>
        <form method="POST" action="/summarize">
            <button type="submit" class="btn btn-primary d-block mx-auto">Summarize</button>
        </form>
        
        {% if summary %}
        <div class="card mt-4">
            <div class="card-body">
                <h3 class="card-title text-success">Summary:</h3>
                <pre class="card-text">{{ summary }}</pre>
                <a href="{{ url_for('download_summary', filename=filename) }}" class="btn btn-success mt-3">Download Summary</a>
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True, port=8080)