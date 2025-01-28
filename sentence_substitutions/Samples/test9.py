import spacy
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
import nltk
from itertools import product
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

# Download necessary NLTK resources
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')

# Load SpaCy's language model
nlp = spacy.load("en_core_web_sm")

# Load the Sentence-BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

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

def generate_sentences(sentence, suggestions):
    """
    Replace each word in the sentence with its suggested words and generate all possible sentences.
    """
    words = sentence.split()
    options = []

    # For each word, replace it with its suggestions or keep the original word if no suggestions exist
    for word in words:
        if word in suggestions:
            options.append([word] + suggestions[word])  # Include the original word and its synonyms
        else:
            options.append([word])  # Keep the word unchanged if no suggestions

    # Generate all combinations of the sentence with substitutions
    all_combinations = product(*options)
    return [" ".join(combination) for combination in all_combinations]

def calculate_semantic_similarity(original_sentence, modified_sentence):
    # Load the pre-trained SentenceTransformer model
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    
    # Encode both sentences
    embeddings1 = model.encode(original_sentence, convert_to_tensor=True)
    embeddings2 = model.encode(modified_sentence, convert_to_tensor=True)
    
    # Compute cosine similarity
    cosine_similarity = util.pytorch_cos_sim(embeddings1, embeddings2)
    
    return cosine_similarity.item()

def process_sentence(sentence):
    """
    Analyze the input sentence and suggest better words, then generate all possible sentences.
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

    # Generate all possible sentences
    possible_sentences = generate_sentences(sentence, suggestions)
    
    print("\nAll Possible Sentences:")
    for i, new_sentence in enumerate(possible_sentences, 1):
        similarity = compute_similarity(sentence, new_sentence)
        print(f"{i}: {new_sentence} (Similarity: {similarity:.4f})")

# Example Usage
user_sentence = "The movie was great but not brilliant"
process_sentence(user_sentence)
