import spacy
import pandas as pd
from fin_bert_analysis import finbertAnalysis, get_recommendation
from emoji_sentiment import load_emoji_data, analyze_emoji_sentiment
from general_sentiment_analysis import analyze
from flask import Flask, request, jsonify
from flask_cors import CORS
import word_suggestions as ss
import word_suggester as ws

app = Flask(__name__)
CORS(app)
def load_financial_terms(csv_file):
    df = pd.read_csv(csv_file, header=0)
    financial_terms = df['term'].tolist()
    return financial_terms


def segment_sentences(paragraph):
    doc = nlp(paragraph)
    return [sent.text for sent in doc.sents]

def classify_sentence(sentence, financial_terms):
    if any(term.lower() in sentence.lower() for term in financial_terms):
        return "financial"
    else:
        return "general"

def extract_emojis(paragraph, emoji_list):
    return [char for char in paragraph if char in emoji_list]


def classify_paragraph(paragraph, emoji_list, emoji_sentiment_data):
    sentences = segment_sentences(paragraph)
    classified_sentences = []
    
    for sentence in sentences:
        classification = classify_sentence(sentence, financial_terms)
        classified_sentences.append((sentence, classification))
    
    extracted_emojis = extract_emojis(paragraph, emoji_list)
    financial_statements = [sentence for sentence, classification in classified_sentences if classification == "financial"]
    
    sentiment_results = [(statement, finbertAnalysis(statement)) for statement in financial_statements]
    recommendations = {
    statement: {
        "sentiment": sentiment[0],
        "recommendation": get_recommendation(sentiment)
    }
    for statement, sentiment in sentiment_results   
    }
    emoji_sentiment = analyze_emoji_sentiment(extracted_emojis, emoji_sentiment_data)
    general_statements = [sentence for sentence, classification in classified_sentences if classification == "general"]
    analyzed_general_statements = [(statement, analyze(statement)) for statement in general_statements]
    
    return classified_sentences, len(extracted_emojis), recommendations, emoji_sentiment, analyzed_general_statements



nlp = spacy.load('en_core_web_sm')
financial_terms = load_financial_terms('financial_terms.csv')
emoji_list, emoji_sentiment_data = load_emoji_data('Emoji_Sentiment_Data_v1.0.csv')


@app.route('/analyze', methods=['POST'])
def analyze_paragraph():
    data = request.get_json()
    paragraph = data.get('paragraph', '')

    classified_results, emoji_count, recommendations, emoji_sentiment, analyzed_general_statements = classify_paragraph(paragraph, emoji_list, emoji_sentiment_data)
    response = {
        "classified_results": [],
        "recommendations": [],
        "general_statements": [],
        "Total Emojis": emoji_count,
        "Overal Emoji Sentiment": emoji_sentiment
    }

    for sentence, classification in classified_results:
        response["classified_results"].append({
            "Sentence": sentence.strip(),
            "Type": classification,
        })
    print("Nad",recommendations)
    for statement, details in recommendations.items():
        response["recommendations"].append({
            "Financial Statement": statement.strip(),
            "Sentiment": details["sentiment"],
            "Recommendation": details["recommendation"]
        })

    for analysis in analyzed_general_statements:
        statement = analysis[0]
        general_analysis = analysis[1][0]
        sentiment = general_analysis['sentiment']
        recommendation = general_analysis['recommendation']

        response["general_statements"].append({
            "General Statement": statement,
            "Sentiment": sentiment,
            "Recommendation": recommendation
        })

    return jsonify(response)

@app.route('/suggestions', methods=['POST'])
def get_suggestions():
    data = request.get_json()

    if 'sentence' not in data:
        return jsonify({"error": "No sentence provided"}), 400

    sentence = data['sentence']
    
    result = ws.process_sentence(sentence)
    
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)