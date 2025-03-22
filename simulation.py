import os
import re
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Retrieve API keys
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not YOUTUBE_API_KEY:
    raise ValueError("YouTube API Key not found. Set it in the .env file.")

if not GOOGLE_API_KEY:
    raise ValueError("Google API Key not found. Set it in the .env file.")

# Initialize AI Model
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.5,
    google_api_key=GOOGLE_API_KEY
)

# Initialize YouTube API Client
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Prompt Template
prmt_temp = """
You are an AI system tasked with generating a structured list of topics for {subject} learning, tailored to the user's inputs.

- Age Group: {age_group}
- Education Level: {education_level}
- Learning Goal: {learning_goal}
- Course Duration: {course_duration}
- Learning Speed: {learning_speed}
- Attention Span & Focus: {focus_level}
- Processing Speed & Learning Adaptability: {processing_speed}

Generate a list of topics in a logical, ordered sequence. Ensure progression aligns with the user's learning speed, attention span, and course duration. Each topic should be listed in numbered order, starting with basics and progressing towards advanced topics.
Age and education level is the main factor in the learning process.
No need to greet or any extra information other than the list.
"""

# Function to generate topics using AI model
def generate_response(inputs):
    formatted_prompt = prmt_temp.format(
        age_group=inputs["age_group"],
        education_level=inputs["education_level"],
        learning_goal=inputs["learning_goal"],
        course_duration=inputs["course_duration"],
        learning_speed=inputs["learning_speed"],
        focus_level=inputs["focus_level"],
        processing_speed=inputs["processing_speed"],
        subject=inputs["subject"]
    )
    return model.invoke(formatted_prompt).content

# Wrap AI function in RunnableLambda
llm_chain = RunnableLambda(generate_response)

# Function to get roadmap (learning topics)
def get_roadmap(inputs):
    response = llm_chain.invoke(inputs)
    return response.strip().split("\n")  # Return as a list of topics

# Function to convert ISO 8601 duration to seconds
def parse_duration(duration_iso):
    pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    match = pattern.fullmatch(duration_iso)
    if not match:
        return 0
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    return hours * 3600 + minutes * 60 + seconds

# Function to fetch video transcript
def get_video_transcript(video_id):
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ' '.join([entry['text'] for entry in transcript_data])
        return transcript if transcript.strip() else None
    except Exception:
        return None

# Function to fetch video details from YouTube
def get_video_details_and_transcript(query, max_results=3):
    video_details = []
    results_count = 0
    next_page_token = None

    while results_count < max_results:
        search_response = youtube.search().list(
            q=query, 
            part='snippet', 
            maxResults=10,
            type='video',
            pageToken=next_page_token
        ).execute()

        for item in search_response['items']:
            if results_count >= max_results:
                break

            video_id = item['id']['videoId']
            video_url = f'https://www.youtube.com/watch?v={video_id}'

            video_data = youtube.videos().list(
                part='snippet,contentDetails',
                id=video_id
            ).execute()

            if not video_data['items']:
                continue

            iso_duration = video_data['items'][0]['contentDetails'].get('duration', None)
            duration_seconds = parse_duration(iso_duration) if iso_duration else None

            transcript = get_video_transcript(video_id)

            if not transcript or len(transcript) <= 500:
                continue  # Ignore short or unavailable transcripts

            video_details.append({
                'video_id': video_id,
                'title': item['snippet']['title'],
                'url': video_url,
                'duration': duration_seconds,
                'transcript': transcript
            })
            
            results_count += 1

        next_page_token = search_response.get('nextPageToken', None)
        if not next_page_token:
            break

    return video_details

# Function to sanitize filenames
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

# Function to save JSON
def save_to_json(data, subject):
    filename = f"C:/Users/gokul/HackFest/gps/src/backend/video_details/video_details_{sanitize_filename(subject)}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Flask route to process form submission
@app.route('/submit-form', methods=['POST'])
def submit_form():
    form_data = request.json
    subjects = ["Web Development", "Mobile App Development", "Data Structures", 
                "Machine Learning", "Object Oriented Programming", "Artificial Intelligence"]

    user_inputs = {
        "age_group": form_data.get("ageGroup", ""),
        "education_level": form_data.get("educationLevel", ""),
        "learning_goal": form_data.get("learningGoals", ""),
        "course_duration": form_data.get("courseDuration", ""),
        "learning_speed": form_data.get("learningSpeed", ""),
        "focus_level": form_data.get("attentionSpan", ""),
        "processing_speed": form_data.get("processingSpeed", ""),
    }

    all_video_details = []

    for subject in subjects:
        user_inputs["subject"] = subject
        topics = get_roadmap(user_inputs)

        subject_videos = []
        for topic in topics[:5]:  # Limit to 5 topics
            subject_videos.extend(get_video_details_and_transcript(topic.strip(), max_results=3))

        save_to_json(subject_videos, subject)
        all_video_details.extend(subject_videos)

    return jsonify({"message": "Video details fetched successfully", "videos": all_video_details})

if __name__ == "__main__":
    app.run(debug=True)
