import os
import json  # Import JSON module to handle array data in data.txt
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
from datetime import datetime, timezone
# Import necessary modules from server/ml_modules
from server.ml_modules.summarization import summarize_text
from server.ml_modules.sentiment_analysis import analyze_sentiment
from server.ml_modules.categorization import categorize_text
from server.ml_modules.keyword_extraction import extract_keywords

# Load environment variables from .env
load_dotenv()

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

def process_feedback_from_text(text):
    """
    Process feedback by summarizing, analyzing sentiment, categorizing, and extracting keywords.
    """
    # Summarization
    summary = summarize_text(text)

    # Sentiment Analysis
    sentiment = analyze_sentiment(text)

    # Categorization
    category = categorize_text(text)

    # Keyword Extraction
    keywords = extract_keywords(text)

    return {
        'summary': summary,
        'sentiment': sentiment,
        'category': category,
        'keywords': keywords
    }

def upload_feedback_to_mongo(file_path):
    """
    Read a JSON array from the text file, process each item, and upload the result to MongoDB.
    """
    try:
        # Read and parse the JSON array from data.txt
        with open(file_path, 'r') as file:
            feedback_list = json.load(file)  # Parse the file content as JSON (list of strings)

        # Process each feedback entry in the array
        for feedback in feedback_list:
            feedback = feedback.strip()  # Clean up any leading/trailing spaces
            if feedback:  # Ensure the feedback is not empty
                # Process the feedback
                feedback_data = process_feedback_from_text(feedback)

                # Add a timestamp
                feedback_data['timestamp'] = datetime.now(timezone.utc)  # Use timezone-aware datetime

                # Insert the feedback into MongoDB
                try:
                    feedback_collection.insert_one(feedback_data)
                    print(f"Successfully inserted feedback: {feedback_data}")
                except Exception as e:
                    print(f"Failed to insert feedback: {e}")

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from {file_path}: {e}")
    except FileNotFoundError as e:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    # Specify the path to your data.txt file within the `scripts` folder
    file_path = '/Users/shravyachepa/Code/medev/server/scripts/data.txt'

    # Call the function to process and upload feedback
    upload_feedback_to_mongo(file_path)
