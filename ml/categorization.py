from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Load the actual review texts from text_test.txt
import numpy as np
import os
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()

# Define possible categories
categories = [
    'Emergency Room Care', 'Surgical Experience', 'Doctor Consultation', 'Nurse Communication', 
    'Hospital Environment & Cleanliness', 'Wait Times', 'Billing and Insurance', 
    'Medical Equipment & Technology', 'Appointment Scheduling', 'Discharge Process', 
    'Medication and Treatment', 'Patient Safety', 'Food and Amenities', 
    'Patient Support Services', 'Communication and Follow-up'
]

# Define keywords for each category
category_keywords = {
    'Doctor Consultation': ['doctor', 'physician', 'consultation', 'diagnosis', 'treatment'],
    'Nurse Communication': ['nurse', 'care', 'attentive', 'nurses', 'communication'],
    'Hospital Environment & Cleanliness': ['clean', 'environment', 'hospital', 'facility'],
    'Wait Times': ['wait', 'long', 'waiting', 'delay', 'time'],
    'Billing and Insurance': ['billing', 'insurance', 'cost', 'payment'],
    'Emergency Room Care': ['emergency room', 'ER', 'urgent', 'emergency'],
    'Surgical Experience': ['surgery', 'operation', 'procedure', 'surgeon'],
    'Medical Equipment & Technology': ['equipment', 'technology', 'machines', 'devices'],
    'Appointment Scheduling': ['appointment', 'schedule', 'booking', 'time'],
    'Discharge Process': ['discharge', 'left', 'released', 'leaving'],
    'Medication and Treatment': ['medication', 'drugs', 'treatment', 'prescription'],
    'Patient Safety': ['safety', 'secure', 'safe', 'protocol'],
    'Food and Amenities': ['food', 'meals', 'dining', 'amenities'],
    'Patient Support Services': ['support', 'counseling', 'therapy', 'assistance'],
    'Communication and Follow-up': ['follow-up', 'call', 'contact', 'communicated']
}
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Define possible categories
categories = [
    'Doctor Consultation', 'Nurse Communication', 'Hospital Environment & Cleanliness', 
    'Wait Times', 'Billing and Insurance', 'Emergency Room Care', 'Surgical Experience', 
    'Medical Equipment & Technology', 'Appointment Scheduling', 'Discharge Process', 
    'Medication and Treatment', 'Patient Safety', 'Food and Amenities', 
    'Patient Support Services', 'Communication and Follow-up'
]

# Function to assign categories based on keyword matching (as defined previously)
def assign_categories(text):
    labels = [0] * len(categories)
    for i, category in enumerate(categories):
        for keyword in category_keywords[category]:
            if keyword.lower() in text.lower():
                labels[i] = 1
    return labels

# Load the review texts
def load_train_texts(file_path):
    with open(file_path, 'r') as file:
        train_texts = file.readlines()
    return train_texts

# Load binary labels for all reviews
def load_train_labels(train_texts):
    return [assign_categories(review) for review in train_texts]

# File path to your text_test.txt
file_path = os.getenv('TRAIN_DATA_PATH')

# Load the training data (51 reviews)
train_texts = load_train_texts(file_path)

# Automatically generate binary labels for all 51 reviews
train_labels = load_train_labels(train_texts)

# Initialize vectorizer and classifier
vectorizer = TfidfVectorizer()

# Use OneVsRestClassifier to handle multi-label classification with MultinomialNB
from sklearn.multiclass import OneVsRestClassifier
classifier = OneVsRestClassifier(MultinomialNB())

# Train the classifier using the actual data
X_train = vectorizer.fit_transform(train_texts)
y_train = np.array(train_labels)  # Ensure train_labels is a numpy array

classifier.fit(X_train, y_train)

# Categorization function to predict multiple categories
def categorize_text(text):
    X = vectorizer.transform([text])
    category_probs = classifier.predict(X)[0]
    assigned_categories = [categories[i] for i in range(len(categories)) if category_probs[i] == 1]
    return assigned_categories
