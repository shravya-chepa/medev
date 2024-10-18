from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
import os
from ml import ml_logic
from blueprints.user import user_bp
from blueprints.admin import admin_bp
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

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

    # Store the result in MongoDB
    try:
        feedback_collection.insert_one(feedback_json)
        print("Successfully inserted feedback into MongoDB")
    except ConnectionFailure as e:
        print(f"Connection Failure: {str(e)}")
        return jsonify({'error': 'Database connection failed', 'details': str(e)}), 500
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500

    return feedback_result

if __name__ == '__main__':
    app.run(debug=True)
