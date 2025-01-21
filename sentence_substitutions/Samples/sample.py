import torch
from transformers import BertTokenizer
from transformers.models.bert.modeling_bert import BertConfig
from torch.nn import functional as F
import json

class BertModelForSuggestion(torch.nn.Module):
    def __init__(self, model_path="bert-base-uncased"):
        super().__init__()
        config = BertConfig.from_pretrained(model_path)
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        self.model = torch.load(model_path)  

    def get_suggestions(self, sentence):
        inputs = self.tokenizer(sentence, return_tensors="pt", padding=True, truncation=True)

        with torch.no_grad():
            outputs = self.model(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                output_hidden_states=True,
                return_dict=True
            )

        logits = outputs.last_hidden_state  

        probabilities = F.softmax(logits, dim=-1)

        suggestions = {}
        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])

        for idx, token in enumerate(tokens):
            top_k = torch.topk(probabilities[0, idx], k=5)
            suggested_tokens = self.tokenizer.convert_ids_to_tokens(top_k.indices)

            if token not in ["[CLS]", "[SEP]", "[PAD]"]:  
                suggestions[token] = {
                    "top_suggestions": suggested_tokens,
                    "probabilities": top_k.values.tolist(),
                }

        return suggestions


model_path = r"C:\Rohit\Projects\Fintech\sentiment_analysis_for_business\fine_tuned_bert"
bert_suggestion_model = BertModelForSuggestion(model_path)

test_sentences = [
    "The company reported a 20% increase in revenue.",
    "Market trends show positive growth this quarter.",
    "He is walking to the park every evening.",
]

for sentence in test_sentences:
    print(f"\nInput Sentence: {sentence}")
    suggestions = bert_suggestion_model.get_suggestions(sentence)
    print(json.dumps(suggestions, indent=4))
