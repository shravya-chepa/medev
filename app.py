from flask import Flask, render_template, jsonify, current_app, request
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

@app.route('/reviews')
def show_reviews():
    return render_template('reviews.html')
@app.route('/fetch_reviews', methods=['GET'])
def fetch_reviews():
    # Fetch Reddit discussions mentioning 'Sharp Hospitals' in San Diego
    subreddit = reddit.subreddit('all')
    search_query = "Sharp Hospital San Diego"
    # Fetching 5 Reddit posts about Sharp Hospital
    processed_comments = []  # To store processed comment data only
    for submission in subreddit.search(search_query, limit=5):
        # Fetch comments for each submission
        submission.comments.replace_more(limit=0)  # Prevent fetching 'more comments'
        for comment in submission.comments.list():
            if len(comment.body) <= 1000:  # Only process comments shorter than 1000 characters
                # Process the comment text to get summary, sentiment, keywords, etc.
                summary = ml_logic.summarize_text(comment.body)
                sentiment = ml_logic.analyze_sentiment(comment.body)
                keywords = ml_logic.extract_keywords(comment.body)
                category = ml_logic.categorize_text(comment.body)
                # Structure the comment data
                comment_data = {
                    "summary": summary,
                    "sentiment": sentiment,
                    "keywords": keywords,
                    "category": category
                }
                # Append the processed comment to the list
                processed_comments.append(comment_data)

    print("processed comments: ", processed_comments)
    return jsonify(processed_comments)  # Return only processed comments as JSON
# Route to save processed comments to MongoDB
@app.route('/process_reviews', methods=['POST'])
def process_reviews():
    reviews = request.json  # Get the processed comments from the frontend
    # Process each review (comment) and store it in MongoDB
    for review in reviews:
        try:
            # Save each processed comment to MongoDB
            feedback_collection.insert_one(review)
            print(f"Successfully inserted comment into MongoDB")
        except ConnectionFailure as e:
            print(f"Connection Failure: {str(e)}")
            return jsonify({'error': 'Database connection failed', 'details': str(e)}), 500
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return jsonify({'error': 'An error occurred', 'details': str(e)}), 500
    return jsonify({'message': 'Comments successfully saved to MongoDB'}), 200

if __name__ == '__main__':
    app.run(debug=True)
