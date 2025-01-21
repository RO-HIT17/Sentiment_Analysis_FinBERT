import torch
import spacy
from transformers import BertTokenizer, BertForMaskedLM
import os
from sentence_transformers import SentenceTransformer, util

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
def mask_words(sentence, top_k=5):
    """
    Mask relevant words in the sentence and return top-k suggestions for each masked word.
    
    Args:
        sentence (str): Input sentence.
        top_k (int): Number of suggestions to return for each masked token.
    
    Returns:
        masked_sentence (str): The sentence with [MASK] tokens.
        suggestions (list): Top-k suggestions for each masked token.
    """
    # Process the sentence with spaCy to get POS tags
    doc = nlp(sentence)
    
    # Mask adjectives and nouns in the sentence and get positions
    masked_sentence = []
    masked_positions = []  # Positions of masked words
    
    for token in doc:
        if token.pos_ in ['NOUN', 'ADJ', 'VERB']:  # Mask nouns, adjectives, verbs
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

# Function to calculate semantic similarity using Sentence Transformers
def calculate_semantic_similarity(original_sentence, modified_sentence):
    # Load the pre-trained SentenceTransformer model
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    
    # Encode both sentences
    embeddings1 = model.encode(original_sentence, convert_to_tensor=True)
    embeddings2 = model.encode(modified_sentence, convert_to_tensor=True)
    
    # Compute cosine similarity
    cosine_similarity = util.pytorch_cos_sim(embeddings1, embeddings2)
    
    return cosine_similarity.item()

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
            # Step 1: Mask words (nouns, adjectives, and verbs)
            masked_sentence, suggestions = mask_words(sentence, top_k=5)
            print(f"Masked Sentence: {masked_sentence}")
            
            # Step 2: Create the modified sentence by replacing masked words with suggestions
            modified_sentence = masked_sentence
            for idx, suggestion_set in enumerate(suggestions):
                best_suggestion = suggestion_set[0]['token']  # Take the best suggestion
                modified_sentence = modified_sentence.replace('[MASK]', best_suggestion, 1)
            
            print(f"Modified Sentence: {modified_sentence}")
            
            # Step 3: Calculate semantic similarity between the original and modified sentence
            similarity_score = calculate_semantic_similarity(sentence, modified_sentence)
            print(f"Semantic Similarity: {similarity_score:.4f}")
            
        except ValueError as ve:
            print(f"Error: {ve}")
        except RuntimeError as re:
            print(f"Error: {re}")
