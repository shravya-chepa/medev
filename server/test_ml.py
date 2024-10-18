from server.summarization import summarize_text
from server.sentiment_analysis import analyze_sentiment
from server.categorization import categorize_text
from server.keyword_extraction import extract_keywords
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import from the ml package
from server.summarization import summarize_text

# Sample text to test the functionality
sample_text = """
I received great care in the Emergency Room today. The nurses were quick to respond to my needs,
and the doctor was very knowledgeable and helpful in explaining my condition.
"""

def test_summarization():
    print("Summarization Result:")
    summary = summarize_text(sample_text)
    print(summary)

def test_sentiment_analysis():
    print("\nSentiment Analysis Result:")
    sentiment = analyze_sentiment(sample_text)
    print(sentiment)

def test_categorization():
    print("\nCategorization Result:")
    category = categorize_text(sample_text)
    print(category)

def test_keyword_extraction():
    print("\nKeyword Extraction Result:")
    keywords = extract_keywords(sample_text)
    print(keywords)

if __name__ == "__main__":
    test_summarization()
    test_sentiment_analysis()
    test_categorization()
    test_keyword_extraction()
