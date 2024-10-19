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
    feedback_collection = db['feedback']  # Set up the collection
    # Store MongoDB connection and collection in app config
    app.config['MONGO_DB'] = db
    app.config['FEEDBACK_COLLECTION'] = feedback_collection
    print("Successfully connected to MongoDB")
except ConnectionFailure as e:
    print(f"Could not connect to MongoDB: {e}")
    exit(1)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')

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

@app.route('/feedbacks', methods=['GET'])
def get_feedbacks():
    # Get the feedback collection from the app config
    feedback_collection = current_app.config['FEEDBACK_COLLECTION']

    try:
        # Fetch all feedback records from MongoDB
        feedback_records = list(feedback_collection.find({}))

        # Convert MongoDB documents to JSON serializable format
        feedbacks = []
        for record in feedback_records:
            record['_id'] = str(record['_id'])  # Convert ObjectId to string for JSON compatibility
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
