import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model 
from sklearn.preprocessing import StandardScaler

#model = load_model('emoji_sentiment_model.h5')

def load_emoji_data(csv_file):
    df = pd.read_csv(csv_file)
    return df['Emoji'].tolist(), df

def preprocess_data(emoji_sentiment_df):
    
    X = emoji_sentiment_df[['Negative', 'Neutral', 'Positive']].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled


def analyze_emoji_sentiment(extracted_emojis, emoji_sentiment_data):
    positive_count = 0
    negative_count = 0
    neutral_count = 0

    
    for emoji in extracted_emojis:
        
        if emoji in emoji_sentiment_data['Emoji'].values:
            sentiment_data = emoji_sentiment_data[emoji_sentiment_data['Emoji'] == emoji].iloc[0]
            negative = sentiment_data['Negative']
            neutral = sentiment_data['Neutral']
            positive = sentiment_data['Positive']

            
            if positive > negative and positive > neutral:
                positive_count += 1
            elif negative > positive and negative > neutral:
                negative_count += 1
            else:
                neutral_count += 1


    if positive_count > negative_count:
        return "Positive"
    elif negative_count > positive_count:
        return "Negative"
    else:
        return "Neutral"


