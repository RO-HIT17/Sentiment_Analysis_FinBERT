import utils
from sentence_semantics import compute_similarity, encode
import spacy

spacy_nlp = spacy.load('en_core_web_sm')

sample_txt = utils.read_txt('C:\\Rohit\\Projects\\Fintech\\sentiment_analysis_for_business\\sws\\files\\sample_text.txt')
standard_terms = utils.read_csv('C:\\Rohit\\Projects\\Fintech\\sentiment_analysis_for_business\\sws\\files\\Standardised terms.csv')

accepted_similarity = 0.3
standard_terms_embeddings = encode(standard_terms)


def process_sentence(sentence_words: list, window_size: int) -> list:
    """
    Analyzes the sentence by sequentially iterating its set of words created with window
    :param sentence_words: a list that contains words from a sentence
    :param window_size: a size of moving window that iterates through sentence words
    :return: a list of suggested improvements based on standardized terms
    """

    accepted_suggestions = []
    start_i, end_i = 0, 0

    while end_i < len(sentence_words):
        end_i = start_i + window_size
        standard_term, score = process_phrase(sentence_words[start_i: end_i])

        if score >= accepted_similarity:
            accepted_suggestions.append([start_i, end_i, standard_term, score])
        start_i += 1

    return accepted_suggestions


def process_phrase(words: list) -> tuple:
    """
    Computes similarity of a sentence words to standardized terms
    :param words: a list of words
    :return: a tuple that contains suggested replacement and its similarity score
    """
    phrase = ' '.join(words)
    suggestions = compute_similarity(phrase, standard_terms, standard_terms_embeddings)
    return suggestions[0]


def filter_suggestions(suggestions: list) -> list:
    """
    Filters suggestions to eliminate repetitive items by searching for the highest similarity score
    :param suggestions:
    :return:
    """
    if len(suggestions) <= 1:
        return suggestions

    filtered_suggestions = []
    index = 0
    temp_suggestion = suggestions[index]

    while index + 1 < len(suggestions):
        if temp_suggestion[2] == suggestions[index + 1][2]:
            if temp_suggestion[3] < suggestions[index + 1][3]:
                temp_suggestion = suggestions[index + 1]
        else:
            filtered_suggestions.append(temp_suggestion)
            temp_suggestion = suggestions[index + 1]
        index += 1
    filtered_suggestions.append(temp_suggestion)

    return filtered_suggestions


def convert_format(sentence_words: list, suggestions: list) -> list:
    """
    Converts suggestions into requested format of [Original Phrase, Suggested Phrase, Similarity Score]
    :param sentence_words: a list of words of a sentence from input text
    :param suggestions: a list of tuples containing detailed information of suggestion
    :return: a list of converted suggestions formatted for submission
    """
    suggestion_pairs = []
    for suggestion in suggestions:
        original_phrase = ' '.join(sentence_words[suggestion[0]: suggestion[1]])
        suggestion_pairs.append((original_phrase, suggestion[2], suggestion[3]))
    return suggestion_pairs


def apply_suggestions(sentence_words: list, suggestions: list):
    """
    Applies suggestions by modifying original sentence and inserting them next to original phrase
    :param sentence_words: a list of words that represent a sentence
    :param suggestions: a list of suggestions
    :return: a modified sentence with applied suggestions
    """
    if len(suggestions) < 1:
        return ' '.join(sentence_words)

    for i, suggestion in enumerate(suggestions):
        insert_phrase = f'<{suggestion[2]}>'
        sentence_words.insert(suggestion[1] + i, insert_phrase)
    sentence = ' '.join(sentence_words)
    return sentence


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

    print(all_suggestions)
    return all_suggestions, modified_sentences


def main():
    pass


if __name__ == '__main__':
    main()

