from flask import Flask, render_template
from dotenv import load_dotenv
import os
from ml import ml_logic
from blueprints.user import user_bp
from blueprints.admin import admin_bp

# Load environment variables
load_dotenv()

# Set up Flask app
app = Flask(__name__)

# Access Google Cloud credentials
google_api_credentials = os.getenv('GOOGLEAPI_CREDENTIALS_PATH')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_api_credentials

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')

@app.route('/')
def home():
    return render_template('home.html')

# ML-related routes (calling ml_logic functions)
@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    return ml_logic.transcribe_audio()

@app.route('/process_feedback', methods=['POST'])
def process_feedback():
    return ml_logic.process_feedback()

if __name__ == '__main__':
    app.run(debug=True)
