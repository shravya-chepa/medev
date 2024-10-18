from transformers import pipeline
import torch

# Initialize summarization pipeline
device = 0 if torch.cuda.is_available() else -1
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=device)

def summarize_text(text):
    # If the text is too short, return it as is (no need for summarization)
    if len(text.split()) < 30:
        return text

    # Dynamically adjust based on input length
    input_length = len(text.split())
    min_length = max(20, input_length // 2)  # Ensure the summary is at least half the input length

    # Perform summarization without a max_length constraint
    summary = summarizer(text, min_length=min_length, do_sample=False)[0]['summary_text']
    return summary
