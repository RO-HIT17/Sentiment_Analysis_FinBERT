# Sentiment Analysis for Business

## Overview
This project provides sentiment analysis for business-related text and emojis. It leverages **Natural Language Processing (NLP)** techniques and **deep learning models** to analyze sentiment from textual data, including emoji-based sentiment analysis.

## Features
- **Text Sentiment Analysis**: Determines the sentiment of a given sentence (positive, negative, neutral).
- **Emoji Sentiment Analysis**: Analyzes the sentiment of emojis present in the text.
- **Word Suggestions**: Suggests better word choices for improved communication.
- **Semantic Similarity Calculation**: Compares modified sentences with the original to ensure minimal meaning distortion.
- **REST API**: Provides an API endpoint for analyzing sentiment and suggesting improvements.

## Technologies Used
- **Python 3.11**
- **Flask** (for API development)
- **spaCy** (for NLP processing)
- **NLTK** (for synonym extraction)
- **Sentence-Transformers** (for semantic similarity calculation)
- **TensorFlow/Keras** (for emoji sentiment analysis)

## Installation
### Prerequisites
Ensure you have Python 3.11 installed. Then install the required dependencies:

```bash
pip install flask spacy nltk sentence-transformers tensorflow
```

Download the required NLP models:
```bash
python -m spacy download en_core_web_sm
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')
```

## Project Structure
```
📂 Sentiment_Analysis_FinBERT
├── 📂 server
│   ├── app.py                     # Flask application
│   ├── emoji_sentiment.py          # Emoji sentiment analysis functions
│   ├── text_processing.py          # Word suggestions & semantic similarity calculations
│   ├── emoji_sentiment_model.h5    # Pre-trained emoji sentiment model
├── requirements.txt                # Project dependencies
├── README.md                       # Project documentation
```

## Usage
### Running the Flask API
```bash
python server/app.py
```

The API will start on `http://127.0.0.1:5000`.

### API Endpoints
#### 1. **Analyze Sentiment**
**Endpoint:** `/analyze`  
**Method:** `POST`

**Request Body:**
```json
{
  "text": "I love this product! 😊"
}
```

**Response:**
```json
{
  "text_sentiment": "positive",
  "emoji_sentiment": "happy",
  "suggestions": {
    "love": ["adore", "cherish", "appreciate"]
  },
  "alternative_sentences": [
    {
      "sentence": "I adore this product! 😊",
      "similarity": 0.95
    }
  ]
}
```

## Troubleshooting
### **TensorFlow Model Loading Issue**
If you encounter an error like:
```
TypeError: Error when deserializing class 'InputLayer'
```
Try using:
```python
import tensorflow as tf
model = tf.keras.models.load_model('emoji_sentiment_model.h5')
```
Alternatively, ensure compatibility by installing TensorFlow 2.11:
```bash
pip install tensorflow==2.11.0
```

## Future Enhancements
- Integrate sentiment visualization.
- Expand emoji sentiment analysis to support more cultural variations.


