import spacy
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
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

    replaced_sentences = generate_replaced_sentences(sentence, suggestions)
    
    print("\nSentences with single word replacements:")
    for i, new_sentence in enumerate(replaced_sentences, 1):
        similarity = calculate_semantic_similarity(sentence, new_sentence)
        if similarity > 0.90:
            print(f"{i}: {new_sentence} (Similarity: {similarity:.4f})")

test_sentences = [
        "The stock market is performing exceptionally well today.",
        "The financial growth of the company increased significantly.",
        "Investors are optimistic about the future of the stock market.",
        "The stock market hasn't changed much!",
    "Sun Shines upon us",
    "I am uncertain about the company’s future growth.",
    "We are seeing tremendous profits this quarter.",
    "The weather is harsh today, and I feel lazy.",
    "The partnership will open up new revenue streams.",
    "There were unexpected losses in Q3.",
    "This year has been fantastic for our investments.",
    "We’re facing serious financial challenges.",
    "The stock hit an all-time high.",
    "The market has been stable recently.",
    "Shareholders are unhappy with the performance.",
    "The quarterly report shows solid growth.",
    "Economic downturns have affected the company.",
    "We are optimistic about the upcoming merger.",
    "Revenue projections were not met.",
    "The company’s future looks bright with the new CEO.",
    "Operational costs have been rising.",
    "Investors have shown increased interest.",
    "The profit margin is higher than last year."
    ]
for user_sentence in test_sentences:
    print("--------------------")
    process_sentence(user_sentence)
    print("--------------------")
#user_sentence = "I am uncertain about the company’s future growth."
#process_sentence(user_sentence) 
