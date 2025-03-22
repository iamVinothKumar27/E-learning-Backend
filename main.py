# main.py
from flask import Flask
from flask_cors import CORS

# Import route handlers from each file
from quiz import app as quiz_app
from simulation import app as simulation_app
from summary import app as summary_app
from meet2 import app as meet_app
from doubtclarification import app as doubt_app

# Create the main Flask app
main_app = Flask(__name__)
CORS(main_app)  # Enable CORS globally

# Register blueprints or mount sub-apps
main_app.register_blueprint(quiz_app, url_prefix="/quiz")
main_app.register_blueprint(simulation_app, url_prefix="/simulation")
main_app.register_blueprint(summary_app, url_prefix="/summary")
main_app.register_blueprint(meet_app, url_prefix="/meet")
main_app.register_blueprint(doubt_app, url_prefix="/doubt")

@main_app.route("/")
def root():
    return {"message": "Backend is live!"}

if __name__ == "__main__":
    main_app.run(host="0.0.0.0", port=10000)