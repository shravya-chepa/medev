from transformers import pipeline
import torch
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Initialize the sentiment analysis model
device = 0 if torch.cuda.is_available() else -1
sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment", device=device)

def analyze_sentiment(text):
    if not text:
        return {"label": "neutral", "score (0-10 scale)": 5}  # Handle empty text input case
    
    try:
        # Analyze sentiment and get label and score
        sentiment = sentiment_analyzer(text)[0]
        
        # Convert star rating to general sentiment label
        if sentiment['label'] in ["1 star", "2 star"]:
            label = "negative"
        elif sentiment['label'] == "3 star":
            label = "neutral"
        elif sentiment['label'] in ["4 star", "5 star"]:
            label = "positive"

        # Manually classify as neutral if the sentiment score is close to 0.5
        if abs(sentiment['score'] - 0.5) < 0.1:  # This can be tuned
            label = "neutral"
        
        # Map the score to a 0-10 scale
        scaled_score = map_score_to_scale(label, sentiment['score'])
        
        return {
            "label": label,
            "score (0-10 scale)": round(scaled_score, 2)
        }

    except Exception as e:
        # Return neutral if there's an error in processing
        return {"label": "neutral", "score (0-10 scale)": 5}

def map_score_to_scale(label, score):
    """
    Map the raw score to a 0-10 scale with intervals of 3
    Negative: 0-3, Neutral: 4-6, Positive: 7-10
    """
    if label == "negative":
        return score * 3  # 0-3 range for negative
    elif label == "neutral":
        return 4 + score * 2  # 4-6 range for neutral
    elif label == "positive":
        return 7 + score * 3  # 7-10 range for positive
