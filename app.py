from flask import Flask, render_template, jsonify, current_app
from dotenv import load_dotenv
import os
from server import ml_logic
from blueprints.user import user_bp
from blueprints.admin import admin_bp
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from server.models import create_feedback_model
from flask_cors import CORS
import logging
import praw  # Reddit API library

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

app.logger.setLevel(logging.DEBUG)

# MongoDB Connection
try:
    client = MongoClient(os.getenv('MONGO_URI'), tlsAllowInvalidCertificates=True)
    db = client['patient_feedback_db']
    feedback_collection = db['feedback']  # Use the same collection for feedback
    app.config['MONGO_DB'] = db
    app.config['FEEDBACK_COLLECTION'] = feedback_collection
    print("Successfully connected to MongoDB")
except ConnectionFailure as e:
    print(f"Could not connect to MongoDB: {e}")
    exit(1)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')

# Reddit API setup
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent=os.getenv('REDDIT_USER_AGENT')
)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/process_feedback', methods=['POST'])
def process_feedback():
    feedback_result = ml_logic.process_feedback()
    feedback_json = feedback_result.get_json()

    print("This is feedback JSON: ", feedback_json)

    # Use the model to create the feedback document
    feedback_document = create_feedback_model(
        category=feedback_json.get("category", []),
        keywords=feedback_json.get("keywords", []),
        sentiment=feedback_json.get("sentiment", {}),
        summary=feedback_json.get("summary", "")
    )

    # Get the feedback collection from the app config
    feedback_collection = current_app.config['FEEDBACK_COLLECTION']

    # Store the result in MongoDB
    try:
        feedback_collection.insert_one(feedback_document)
        print("Successfully inserted feedback into MongoDB")
    except ConnectionFailure as e:
        print(f"Connection Failure: {str(e)}")
        return jsonify({'error': 'Database connection failed', 'details': str(e)}), 500
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500

    return feedback_result

@app.route('/reddit_feedback', methods=['GET'])
def get_reddit_feedback():
    """
    Collects Reddit feedback from specific subreddits and stores it in the same 'feedback' collection.
    """
    feedback_collection = current_app.config['FEEDBACK_COLLECTION']
    subreddits = ['healthcare', 'patientfeedback', 'medicine']  # Subreddits to scrape

    try:
        for subreddit in subreddits:
            subreddit_instance = reddit.subreddit(subreddit)

            # Fetching the top 5 posts from each subreddit
            for submission in subreddit_instance.hot(limit=5):
                reddit_document = {
                    'category': ['Reddit'],
                    'keywords': submission.title.split(),  # Use title as keywords
                    'sentiment': {},  # Placeholder for sentiment analysis (can be processed later)
                    'summary': submission.selftext[:200],  # Summary from the first 200 characters
                    'original_data': {
                        'title': submission.title,
                        'text': submission.selftext,
                        'score': submission.score,
                        'url': submission.url,
                        'created_utc': submission.created_utc
                    }
                }

                # Insert the Reddit post into the same feedback collection
                feedback_collection.insert_one(reddit_document)

        return jsonify({'message': 'Reddit feedback successfully collected and stored in feedback collection'}), 200
    except Exception as e:
        print(f"An error occurred while fetching Reddit feedback: {str(e)}")
        return jsonify({'error': 'Failed to collect Reddit feedback', 'details': str(e)}), 500

@app.route('/feedbacks', methods=['GET'])
def get_feedbacks():
    feedback_collection = current_app.config['FEEDBACK_COLLECTION']

    try:
        feedback_records = list(feedback_collection.find({}))
        feedbacks = []
        for record in feedback_records:
            record['_id'] = str(record['_id'])
            feedbacks.append(record)

        return jsonify(feedbacks), 200
    except ConnectionFailure as e:
        print(f"Connection Failure: {str(e)}")
        return jsonify({'error': 'Database connection failed', 'details': str(e)}), 500
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
