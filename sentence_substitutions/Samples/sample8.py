import torch
import spacy
from transformers import BertTokenizer, BertForMaskedLM
import os

# Load spaCy model for POS tagging
nlp = spacy.load('en_core_web_sm')

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
def mask_nouns(sentence, top_k=5):
    """
    Mask nouns in the sentence and return top-k suggestions for each masked word.
    
    Args:
        sentence (str): Input sentence.
        top_k (int): Number of suggestions to return for each masked token.
    
    Returns:
        list of dict: A list of dictionaries with token and prediction score for each masked word.
    """
    # Process the sentence with spaCy to get POS tags
    doc = nlp(sentence)
    
    # Replace nouns with [MASK]
    masked_sentence = []
    masked_positions = []  # Positions of masked words
    
    for token in doc:
        if token.pos_ in ['NOUN', 'PROPN']:  # Mask nouns and proper nouns
            masked_sentence.append('[MASK]')
            masked_positions.append(token.i)
        else:
            masked_sentence.append(token.text)
    
    # Join the sentence back into a string
    masked_sentence_str = ' '.join(masked_sentence)
    
    # Tokenize the masked sentence
    inputs = tokenizer(masked_sentence_str, return_tensors="pt")
    
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
        filtered_suggestions = []
        
        for token in top_k_tokens:
            decoded_token = tokenizer.decode([token])
            filtered_suggestions.append({
                "token": decoded_token,
                "score": token_predictions[token].item(),
            })
        
        suggestions.append(filtered_suggestions)
    
    return masked_sentence_str, suggestions

# Testing the model
if __name__ == "__main__":
    # Input sentences for testing
    test_sentences = [
        "The stock market is performing exceptionally well today.",
        "The financial growth of the company increased significantly.",
        "Investors are optimistic about the future of the stock market.",
    ]
    
    for sentence in test_sentences:
        print(f"\nInput Sentence: {sentence}")
        try:
            masked_sentence, suggestions = mask_nouns(sentence, top_k=5)
            print(f"Masked Sentence: {masked_sentence}")
            for i, suggestion_set in enumerate(suggestions, 1):
                print(f"Suggestions for [MASK] {i}:")
                for suggestion in suggestion_set:
                    print(f"  {suggestion['token']} (Score: {suggestion['score']:.4f})")
        except ValueError as ve:
            print(f"Error: {ve}")
        except RuntimeError as re:
            print(f"Error: {re}")
