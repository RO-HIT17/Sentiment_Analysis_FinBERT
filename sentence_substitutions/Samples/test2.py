import spacy
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
import nltk

# Download necessary NLTK resources
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')

# Load SpaCy's language model
nlp = spacy.load("en_core_web_sm")

def get_synonyms(word):
    """
    Get a list of synonyms for a given word from WordNet.
    """
    synonyms = set()
    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            if lemma.name() != word:
                synonyms.add(lemma.name().replace("_", " "))
    return list(synonyms)

def suggest_better_words(sentence):
    """
    Analyze a sentence and suggest more apt words for each word in the sentence.
    """
    doc = nlp(sentence)
    suggestions = {}

    for token in doc:
        if token.is_stop or token.is_punct:
            continue  # Skip stopwords and punctuation
        
        word_synonyms = get_synonyms(token.text)
        if word_synonyms:
            # Add to suggestions dictionary
            suggestions[token.text] = word_synonyms[:5]  # Limit to 5 suggestions
    
    return suggestions

def process_sentence(sentence):
    """
    Analyze the input sentence and suggest better words.
    """
    print("\nOriginal Sentence:")
    print(sentence)
    
    suggestions = suggest_better_words(sentence)
    
    if not suggestions:
        print("\nNo suggestions found. The sentence is already optimal!")
        return
    
    print("\nSuggestions for improvement:")
    for word, synonyms in suggestions.items():
        print(f"Word: {word}")
        print(f"Suggestions: {', '.join(synonyms)}")

# Example Usage
user_sentence = "The stock market is performing exceptionally well today."
process_sentence(user_sentence)
