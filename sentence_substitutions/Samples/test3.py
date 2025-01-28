import spacy
from nltk.corpus import wordnet
from transformers import pipeline

# Load NLP models
nlp = spacy.load("en_core_web_sm")
text_generator = pipeline("fill-mask", model="bert-base-uncased")

def suggest_words(sentence):
    doc = nlp(sentence)
    suggestions = {}
    
    for token in doc:
        if token.pos_ in ["NOUN", "VERB", "ADJ"]:
            # Get synonyms
            synonyms = [syn.name().replace('_', ' ') for syn in wordnet.synsets(token.text)]
            # Contextual suggestions using BERT
            bert_suggestions = [res['token_str'] for res in text_generator(f"{sentence.replace(token.text, '[MASK]')}")[:3]]
            
            suggestions[token.text] = {
                "synonyms": synonyms[:3],
                "contextual": bert_suggestions
            }
    
    return suggestions

# Example usage
sentence = "The movie was good and interesting."
suggestions = suggest_words(sentence)
print(suggestions)
