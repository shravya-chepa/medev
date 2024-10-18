from google.cloud import speech
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import base64
import torch
import nltk
from flask import request, jsonify

# Initialize NLTK
nltk.download('punkt')
nltk.download('stopwords')

# Set up NLP models
device = 0 if torch.cuda.is_available() else -1
summarizer = pipeline("summarization", device=device)
sentiment_analyzer = pipeline("sentiment-analysis", device=device)

# Google Cloud Speech client
speech_client = speech.SpeechClient()

# Classification model
vectorizer = TfidfVectorizer()
classifier = MultinomialNB()

# Sample training data for classification (replace with real data)
train_texts = [
    "I received great care in the Emergency Room today...",
    "I went to the Emergency Room to get seen for my heart...",
    "I had an angioplasty under the care of Dr Justin Parizo...",
    "I was treated for a severe, and necessary EMERGENCY SURGERY..."
]
train_labels = ['Billing', 'Insurance', 'Hospital Maintenance', 'Doctor Consultation']
X_train = vectorizer.fit_transform(train_texts)
classifier.fit(X_train, train_labels)

def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    audio_content = audio_file.read()
    
    # Encode audio content
    audio_content_base64 = base64.b64encode(audio_content).decode('utf-8')
    audio = speech.RecognitionAudio(content=audio_content_base64)
    
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,  # Set sample rate if known
        language_code="en-US",
    )

    response = speech_client.recognize(config=config, audio=audio)
    
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript

    return jsonify({'transcript': transcript})

def process_feedback():
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # Summarization
    summary = summarizer(text, max_length=100, min_length=30, do_sample=False)[0]['summary_text']

    # Sentiment Analysis
    sentiment = sentiment_analyzer(text)[0]

    # Categorization
    category = classify_text(text)

    # Keyword Extraction
    keywords = extract_keywords(text)

    return jsonify({
        'summary': summary,
        'sentiment': sentiment,
        'category': category,
        'keywords': keywords
    })

def classify_text(text):
    X = vectorizer.transform([text])
    category = classifier.predict(X)[0]
    return category

def extract_keywords(text):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    keywords = [word for word in word_tokens if word.lower() not in stop_words and word.isalnum()]
    return keywords[:10]
