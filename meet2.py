from flask import Flask, render_template_string, request, jsonify, redirect
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

app = Flask(__name__)

# Google API Configuration
SERVICE_ACCOUNT_FILE = "C:/Users/gokul/HackFest/gps/src/backend/service_account.json"  # Ensure this file exists
CALENDAR_ID = "ramrakshitha267@gmail.com"  # Replace with your Google Calendar ID
SPACE_ID = "AAAAWEYV8Gg"  # Replace with your actual Google Chat space ID

# Load credentials
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=[
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/chat.messages.create",
    ],
)

def get_upcoming_events():
    """Fetch upcoming Google Calendar events."""
    try:
        service = build("calendar", "v3", credentials=credentials)
        now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        events_result = (
            service.events()
            .list(
                calendarId=CALENDAR_ID,
                timeMin=now,
                maxResults=5,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        return events
    except Exception as e:
        return []

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Meet & Chat</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
        button { background-color: #4285F4; color: white; border: none; padding: 10px 20px; font-size: 16px; cursor: pointer; margin: 10px; }
        button:hover { background-color: #357ae8; }
        input { padding: 8px; margin: 5px; width: 200px; }
        #meetings { margin-top: 20px; text-align: left; display: inline-block; }
    </style>
</head>
<body>
    <h1>Google Meet & Mentor Chat</h1>
    <button onclick="scheduleMeeting()">Schedule Meeting</button>
    <button onclick="joinMeeting()">Join Meeting</button>
    <button onclick="chatWithMentor()">Chat with Mentor</button>    

    <div id="chatSection" style="display:none;">
        <input type="email" id="mentorEmail" placeholder="Enter Mentor's Email" required>
        <input type="text" id="message" placeholder="Type a message" required>
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
        function scheduleMeeting() {
            window.location.href = "/schedule";
        }

        function joinMeeting() {
            window.location.href = "/join";
        }

        function chatWithMentor() {
            window.open("https://chat.google.com/", "_blank"); // Open Google Chat in a new tab
        }

        function sendMessage() {
            var email = document.getElementById("mentorEmail").value;
            var message = document.getElementById("message").value;

            fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: email, text: message })
            })
            .then(response => response.json())
            .then(data => alert("Message Sent: " + data.status))
            .catch(error => console.error("Error:", error));
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    events = get_upcoming_events()
    meetings = [
        {
            "summary": event.get("summary", "No Title"),
            "start": event["start"].get("dateTime", event["start"].get("date")),
            "link": event.get("hangoutLink", "https://meet.google.com/new"),
        }
        for event in events
    ]
    return render_template_string(HTML_TEMPLATE, meetings=meetings)

@app.route("/schedule")
def schedule():
    now = datetime.utcnow().isoformat() + "Z"
    google_calendar_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text=Google+Meet+Meeting&dates={now}/{now}&details=Join+the+meeting+here:&location=https://meet.google.com/new"
    return redirect(google_calendar_url)

@app.route("/join")
def join():
    return redirect("https://meet.google.com/new")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message_text = data.get("text", "")

    if not message_text:
        return jsonify({"status": "Message cannot be empty"}), 400

    # Refresh token
    credentials.refresh(requests.Request())

    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json",
    }

    # Google Chat API URL
    chat_url = f"https://chat.googleapis.com/v1/spaces/{SPACE_ID}/messages"
    chat_payload = {"text": message_text}

    response = requests.post(chat_url, json=chat_payload, headers=headers)

    if response.status_code == 200:
        return jsonify({"status": "Message sent successfully!"})
    else:
        return jsonify({"status": "Failed to send message", "error": response.text}), response.status_code

if __name__ == "__main__":
    app.run(debug=True, port=5500)  # Running on port 5500 instead of 5000 or 8080
