# Text Improvement Engine
A tool that analyses a given text and suggests improvements based on the similarity to a list of standardised phrases. 
These standardised phrases represent the ideal way certain concepts should be articulated, and the tool recommends
changes to align the input text closer to these standards.

## Technology
Word Embedding and Cosine Similarity are applied. A pre-trained language model finds phrases in the input text 
that are semantically similar to any of the standardised phrases.

A pre-trained model is a sentence-transformers model: It maps sentences & paragraphs to a 768 dimensional dense 
vector space and was designed for semantic search. It has been trained on 500k (query, answer) pairs from 
the MS MARCO Passages dataset. 

It is implemented using HuggingFace Transformers. First, input is passed through the transformer model, then 
the correct pooling-operation is applied on-top of the contextualized word embeddings.

Next, Cosine Similarity is applied to compute similarity between embeddings

## Setup
Use Conda to create environment. Run the following command
```bash
conda env create -f environment.yml
```

## Usage 
Run the following command to open UI for text input. 
```bash
python ui.py
```

## User Interface
Once you run the previous command, it will open UI Window which allows interaction.
![screenshot.jpg](pics%2Fscreenshot.jpg)

## Processing Approach
Since the input paragraph length could be long, it needs to be chunked before being compared. 
Therefore, first, input text is divided into sentences to process each sentence separately. 
This makes sure that replacements are not overlapped between sentences, but applied with one.

To find suggestions within a sentence, a sliding window concept used. 
A window takes 3 words from a sentence, combine them into a phrase and perform similarity measures 
with all standardized terms. Give a similarity threshold = 0.3, it is decided whether a suggestion is taken or not. 
Next, overlapped suggestions are removed. 

The main function that process the request is analyze_txt() in improve_txt.py

```python
def analyze_txt(user_txt: str) -> [list, list]:
    """
    Analyzes the input text and returns suggestions based on standardized terms to improve input text
    :param user_txt: an input text provided by user they wish to analyze
    :return: a list of suggestions to replace phrases in the input text with their more "standard" versions.
            Each suggestion shows the original phrase, the recommended replacement, and the similarity score
             a list of modified sentences with applied suggestions
    """
    sentences = spacy_nlp(user_txt).sents
    all_suggestions = []
    modified_sentences = []

    for sent_i, sentence in enumerate(sentences):

        sentence_words = sentence.text.split()
        suggestions = process_sentence(sentence_words, window_size=3)
        suggestions = filter_suggestions(suggestions)
        suggestion_pairs = convert_format(sentence_words, suggestions)

        all_suggestions.append([sentence.text, suggestion_pairs])
        modified_sentences.append(apply_suggestions(sentence_words, suggestions))

    return all_suggestions, modified_sentences
```

