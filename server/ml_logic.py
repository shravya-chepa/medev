import sys
sys.path.append('..')  # Adds the parent directory to the system path

from flask import request, jsonify
from server.summarization import summarize_text
from server.sentiment_analysis import analyze_sentiment
from server.categorization import categorize_text
from server.keyword_extraction import extract_keywords

def process_feedback():
    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # Summarization
    summary = summarize_text(text)

    # Sentiment Analysis
    sentiment = analyze_sentiment(text)

    # Categorization
    category = categorize_text(text)

    # Keyword Extraction
    keywords = extract_keywords(text)
    print(keywords,summary,sentiment, category)

    json_res = jsonify({
        'summary': summary,
        'sentiment': sentiment,
        'category': category,
        'keywords': keywords
    })

    print("this is json res: ", json_res)
    return json_res

# Load text from text_test.txt
def process_reviews_from_file(file_path):
    with open(file_path, 'r') as file:
        reviews = file.readlines()
    
    all_feedback = []
    for review in reviews:
        feedback = process_feedback_from_text(review.strip())
        all_feedback.append(feedback)
    
    return all_feedback

def process_feedback_from_text(text):
    # Summarize, analyze sentiment, categorize, and extract keywords
    summary = summarize_text(text)
    sentiment = analyze_sentiment(text)
    category = categorize_text(text)
    keywords = extract_keywords(text)

    return {
        'summary': summary,
        'sentiment': sentiment,
        'category': category,
        'keywords': keywords
    }
