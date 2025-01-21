import torch
from transformers import BertTokenizer, BertForMaskedLM
import os

# Specify the path to your fine-tuned model
model_path = r"C:\Rohit\Projects\Fintech\sentiment_analysis_for_business\fine_tuned_bert"

# Check if the model path exists
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model directory not found at: {model_path}")

# Load the tokenizer and model
try:
    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = BertForMaskedLM.from_pretrained(model_path)
    print("Model and tokenizer loaded successfully!")
except Exception as e:
    raise RuntimeError(f"Error loading the model: {e}")

# Set the model to evaluation mode
model.eval()

# Function to predict masked words
def get_suggestions(sentence, top_k=5):
    """
    Predicts the top-k suggestions for the masked word(s) in the sentence.
    
    Args:
        sentence (str): Input sentence with one or more [MASK] tokens.
        top_k (int): Number of suggestions to return for each masked token.
    
    Returns:
        list of dict: A list of dictionaries with token and prediction score.
    """
    if "[MASK]" not in sentence:
        raise ValueError("The input sentence must contain at least one [MASK] token.")
    
    # Tokenize the input
    inputs = tokenizer(sentence, return_tensors="pt")
    
    # Get predictions from the model
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Get predictions for the masked tokens
    masked_indices = (inputs["input_ids"] == tokenizer.mask_token_id).nonzero(as_tuple=True)[1]
    predictions = outputs.logits[0, masked_indices]
    
    # Decode and return the top-k predictions for each masked token
    suggestions = []
    for token_predictions in predictions:
        top_k_tokens = torch.topk(token_predictions, top_k).indices
        suggestions.append([
            {"token": tokenizer.decode([token]), "score": token_predictions[token].item()}
            for token in top_k_tokens
        ])
    return suggestions

# Testing the model
if __name__ == "__main__":
    # Input sentences for testing
    test_sentences = [
        "The stock market is [MASK].",
        "The [MASK] of the company increased significantly.",
        "Investors are [MASK] about the future.",
    ]
    
    for sentence in test_sentences:
        print(f"\nInput Sentence: {sentence}")
        try:
            suggestions = get_suggestions(sentence, top_k=5)
            for i, suggestion_set in enumerate(suggestions, 1):
                print(f"Suggestions for [MASK] {i}:")
                for suggestion in suggestion_set:
                    print(f"  {suggestion['token']} (Score: {suggestion['score']:.4f})")
        except ValueError as ve:
            print(f"Error: {ve}")
        except RuntimeError as re:
            print(f"Error: {re}")
