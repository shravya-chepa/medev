from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import os
from server import ml_logic  # Assuming ml_logic contains your processing functions
from blueprints.user import user_bp
from blueprints.admin import admin_bp
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import praw  # Reddit API wrapper

# Load environment variables from .env
load_dotenv()

# Set up Flask app
app = Flask(__name__)

# Get the MongoDB URI from environment variables (use the standard connection string)
mongo_uri = os.getenv('MONGO_URI')

# Connect to MongoDB using the standard connection string with SSL verification disabled
try:
    client = MongoClient(mongo_uri, tlsAllowInvalidCertificates=True)  # Disable SSL verification
    print("Successfully connected to MongoDB")
except ConnectionFailure as e:
    print(f"Could not connect to MongoDB: {e}")
    exit(1)  # Exit if MongoDB connection fails

# Set up the database and collection
db = client['patient_feedback_db']
feedback_collection = db['feedback']

# Configure PRAW with Reddit credentials
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')

@app.route('/')
def home():
    return render_template('home.html')

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
