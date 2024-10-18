# models.py
from datetime import datetime, timezone

# Define the model for feedback
def create_feedback_model(category, keywords, sentiment, summary):
    return {
        "category": category,             # Array of categories
        "keywords": keywords,             # Array of keywords
        "sentiment": sentiment,           # Sentiment object
        "summary": summary,               # Feedback summary
        "timestamp": datetime.now(timezone.utc)    # Timestamp for when feedback is added
    }
