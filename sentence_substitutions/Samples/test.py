import spacy
def analyze_txt(user_txt: str):
    """
    Analyzes the input text and returns suggestions based on standardized terms to improve input text
    :param user_txt: an input text provided by user they wish to analyze
    :return: a list of suggestions to replace phrases in the input text with their more "standard" versions.
            Each suggestion shows the original phrase, the recommended replacement, and the similarity score
             a list of modified sentences with applied suggestions
    """
    sentences = spacy(user_txt).sents
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
print(analyze_txt("The movie was good and interesting."))