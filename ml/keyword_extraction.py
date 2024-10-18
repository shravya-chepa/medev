import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import ssl
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"


try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')
nltk.download('stopwords')

def extract_keywords(text):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    keywords = [word for word in word_tokens if word.lower() not in stop_words and word.isalnum()]
    return keywords[:10]
