from transformers import pipeline
import torch

# Initialize sentiment analysis pipeline
device = 0 if torch.cuda.is_available() else -1
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", device=device)


def analyze_sentiment(text):
    sentiment = sentiment_analyzer(text)[0]
    return sentiment
