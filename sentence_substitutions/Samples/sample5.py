import torch
from transformers import BertTokenizer, BertForMaskedLM

# Load your fine-tuned model and tokenizer
model_path = r"C:\Rohit\Projects\Fintech\sentiment_analysis_for_business\fine_tuned_bert"

try:
    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = BertForMaskedLM.from_pretrained(model_path)
    print("Model and tokenizer loaded successfully!")
except Exception as e:
    raise RuntimeError(f"Error loading the model: {e}")

# Set the model to evaluation mode
model.eval()

def suggest_replacements(sentence, top_k=3):
    """
    Suggests replacement words for each token in a given sentence.

    Args:
        sentence (str): Input sentence.
        top_k (int): Number of suggestions for each word.

    Returns:
        dict: A dictionary where keys are words and values are suggestions.
    """
    # Tokenize the sentence and encode into token IDs
    tokens = tokenizer.tokenize(sentence)
    token_ids = tokenizer.convert_tokens_to_ids(tokens)

    # Mask each word one by one
    suggestions = {}
    for i in range(len(tokens)):
        # Create a masked version of the sentence
        masked_token_ids = token_ids[:]
        masked_token_ids[i] = tokenizer.mask_token_id  # Replace the current token with [MASK]

        # Convert to tensor
        input_ids = torch.tensor([masked_token_ids])

        # Get predictions from the model
        with torch.no_grad():
            outputs = model(input_ids)
        logits = outputs.logits

        # Get the top-k predictions for the masked token
        masked_index = i
        predictions = logits[0, masked_index]
        top_k_indices = torch.topk(predictions, top_k).indices.tolist()
        top_k_tokens = [tokenizer.decode([idx]) for idx in top_k_indices]

        # Exclude the original token from suggestions
        original_token = tokens[i]
        filtered_suggestions = [token for token in top_k_tokens if token != original_token]
        
        if filtered_suggestions:
            suggestions[original_token] = filtered_suggestions

    return suggestions


if __name__ == "__main__":
    # Input sentence for testing
    input_sentence = "The stock market is performing rebuts well today."
    
    print(f"Input Sentence: {input_sentence}")
    suggestions = suggest_replacements(input_sentence, top_k=3)
    
    print("\nSuggestions:")
    for word, replacements in suggestions.items():
        print(f"Word: {word}")
        print(f"Replacements: {', '.join(replacements)}")
