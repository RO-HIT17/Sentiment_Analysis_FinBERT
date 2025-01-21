from transformers import BertTokenizer, BertForMaskedLM
import torch
# Path to the fine-tuned model directory
model_path = r"C:\Rohit\Projects\Fintech\sentiment_analysis_for_business\fine_tuned_bert"

# Load the tokenizer and model
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertForMaskedLM.from_pretrained(model_path)

# Example sentence for testing
sentence = "The company reported a 20% increase in revenue."

# Tokenize and encode input
inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True)

# Perform inference
with torch.no_grad():
    outputs = model(**inputs)

# Extract predictions
logits = outputs.logits
print("Logits shape:", logits.shape)
