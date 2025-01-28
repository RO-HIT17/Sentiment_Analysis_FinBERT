import spacy
from nltk.corpus import wordnet as wn
import nltk
from sentence_transformers import SentenceTransformer, util

nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')

nlp = spacy.load("en_core_web_sm")

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_synonyms(word):
    synonyms = set()
    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            if lemma.name() != word:
                synonyms.add(lemma.name().replace("_", " "))
    return list(synonyms)

def suggest_better_words(sentence):
    doc = nlp(sentence)
    suggestions = {}

    for token in doc:
        if token.is_stop or token.is_punct:
            continue  
        
        word_synonyms = get_synonyms(token.text)
        if word_synonyms:
            suggestions[token.text] = word_synonyms[:5]  
    
    return suggestions

def generate_replaced_sentences(sentence, suggestions):
    words = sentence.split()
    replaced_sentences = []

    for word in words:
        if word in suggestions:
            for synonym in suggestions[word]:
                new_sentence = sentence.replace(word, synonym)
                replaced_sentences.append(new_sentence)
    
    return replaced_sentences

def calculate_semantic_similarity(original_sentence, modified_sentence):
    embeddings1 = model.encode(original_sentence, convert_to_tensor=True)
    embeddings2 = model.encode(modified_sentence, convert_to_tensor=True)
    
    cosine_similarity = util.pytorch_cos_sim(embeddings1, embeddings2)
    
    return cosine_similarity.item()

def process_sentence(sentence):
    """
    Analyze the input sentence and suggest better words, then generate all possible sentences with one word replaced.
    """
    suggestions = suggest_better_words(sentence)
    
    if not suggestions:
        return {"message": "No suggestions found. The sentence is already optimal!"}

    replaced_sentences = generate_replaced_sentences(sentence, suggestions)
    
    results = []
    
    for new_sentence in replaced_sentences:
        similarity = calculate_semantic_similarity(sentence, new_sentence)
        if similarity > 0.90:  
            result = {
                "original_sentence": sentence,
                "modified_sentence": new_sentence,
                "similarity": round(similarity, 4)
            }
            results.append(result)
    
    return {"suggestions": results}