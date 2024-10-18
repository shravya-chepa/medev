

# Feedback Processing API

## Overview
This API processes audio feedback and provides text analysis, including transcription, summarization, sentiment analysis, categorization, and keyword extraction. Built using Flask, it utilizes Google Cloud Speech-to-Text for audio processing and various NLP models for text analysis.

## Prerequisites
Before running this application, ensure you have the following installed:

- Latest Python version
- Latest pip (Python package installer)
- Google Cloud account (with a Speech-to-Text API key)

## Getting Started

### 1. Clone the Repository
Clone this repository to your local machine using:
```bash
git clone https://github.com/shravya-chepa/medev.git
cd medev
```

### 2. Set Up a Virtual Environment
Create and activate a virtual environment:
```bash
# For macOS/Linux
python3 -m venv env
source env/bin/activate

# For Windows
python -m venv env
.\env\Scripts\activate
```

### 3. Install Required Packages
Install the necessary packages using `pip`:
```bash
pip install -r requirements.txt
```

### 4. Set Up Google Cloud Credentials
Create a service account in Google Cloud with access to the Speech-to-Text API and download the credentials JSON file. Save the file as `secret_key.json` in the root of your project directory.

Set the environment variable for Google Cloud credentials:
```bash
export GOOGLE_APPLICATION_CREDENTIALS='secret_key.json'
```
For Windows, use:
```bash
set GOOGLE_APPLICATION_CREDENTIALS=secret_key.json
```

### 5. Set up environment variable for file path of google credentials
Create a .env file in the root folder and set its content as
```
GOOGLEAPI_CREDENTIALS_PATH=YOUR-PATH-HERE
```

### 6. Run the Application
Start the Flask application:
```bash
python app.py
```
The API will be accessible at `http://127.0.0.1:5000/`.

### 7. API Endpoints
- **Home**: 
  - `GET /` - Returns a welcome message.
  
- **Transcribe Audio**:
  - `POST /transcribe` - Expects an audio file. Returns the transcribed text.

- **Process Feedback**:
  - `POST /process_feedback` - Expects a JSON body with a text field. Returns the summarized text, sentiment analysis, category, and keywords.
  In Postman, start a new POST request- http://127.0.0.1:5000/process_feedback
  In Body, select raw and give json of the form
  ```
  {
    "text": "Your feedback here"
  }
  ```


### 8. Stop the Application
To stop the Flask server, you can press `Ctrl + C` in the terminal where the server is running.


## 4. Start MongoDB Manually (If Needed)
If you don’t want MongoDB running as a background service, you can start it manually with:

mongod --config /opt/homebrew/etc/mongod.conf
## 5. Stop MongoDB (Optional)
If you ever need to stop MongoDB, you can use:

brew services stop mongodb/brew/mongodb-community

