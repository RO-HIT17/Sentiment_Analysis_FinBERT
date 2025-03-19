import requests
import json
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import google.generativeai as genai

# Download necessary resources
nltk.download("vader_lexicon")

# Configure Gemini API
genai.configure(api_key="AIzaSyD30Q3CDEjLT8nWoJYb63h3rOL18KK6QCc") # Replace with your actual API key
model = genai.GenerativeModel('gemini-2.0-flash')

def fetch_reviews(api_key, url):
    """Fetch reviews from Amazon using ScraperAPI."""
    payload = {
        'api_key': api_key,
        'url': url,
        'output_format': 'json',
        'autoparse': 'true'
    }
    response = requests.get('https://api.scraperapi.com/', params=payload)
    return response.json()

def extract_reviews(data):
    """Extract reviews from JSON data."""
    if isinstance(data, dict) and "reviews" in data:
        return [review["review"] for review in data["reviews"] if "review" in review]
    else:
        return []

def summarize_reviews_gemini(reviews, num_sentences=3):
    """Summarize customer reviews using Gemini API."""
    if not reviews:
        return "No reviews available."
    text = " ".join(reviews)
    prompt = f"Summarize the following customer reviews in {num_sentences} sentences:\n\n{text}"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error summarizing with Gemini: {e}"

def analyze_sentiment(reviews):
    """Perform sentiment analysis using VADER."""
    sia = SentimentIntensityAnalyzer()
    sentiments = [sia.polarity_scores(review)["compound"] for review in reviews]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    return avg_sentiment

def compare_products_gemini(url1, url2, api_key):
    """Compare two Amazon products based on reviews using Gemini."""
    print("Fetching reviews for product 1...")
    data1 = fetch_reviews(api_key, url1)
    reviews1 = extract_reviews(data1)
    summary1 = summarize_reviews_gemini(reviews1)
    sentiment1 = analyze_sentiment(reviews1)

    print("Fetching reviews for product 2...")
    data2 = fetch_reviews(api_key, url2)
    reviews2 = extract_reviews(data2)
    summary2 = summarize_reviews_gemini(reviews2)
    sentiment2 = analyze_sentiment(reviews2)

    print("\n🔹 Product 1 Review Summary:\n", summary1)
    print("🔹 Product 1 Sentiment Score:", round(sentiment1, 2))
    print("\n🔹 Product 2 Review Summary:\n", summary2)
    print("🔹 Product 2 Sentiment Score:", round(sentiment2, 2))

    if sentiment1 > sentiment2:
        print("\n✅ Product 1 has better overall sentiment!")
        prompt = f"Given the following review summaries:\nProduct 1: {summary1}\nProduct 2: {summary2}\nExplain why product 1 has better overall sentiment in 5 lines"
        response = model.generate_content(prompt)
        print("🔹 Why Product 1 is better:\n", response.text)
    elif sentiment2 > sentiment1:
        print("\n✅ Product 2 has better overall sentiment!")
        prompt = f"Given the following review summaries:\nProduct 1: {summary1}\nProduct 2: {summary2}\nExplain why product 2 has better overall sentiment in 5 lines"
        response = model.generate_content(prompt)
        print("🔹 Why Product 2 is better:\n", response.text)
    else:
        print("\n⚖️ Both products have similar sentiment scores.")
        print("🔹 Strengths of Product 1:", summary1)
        print("🔹 Strengths of Product 2:", summary2)

if __name__ == "__main__":
    API_KEY = '29ad67281f2f050c70a218b301fd1164' # Replace with your ScraperAPI key
    URL1 = 'https://www.amazon.in/Daikin-Inverter-Display-Technology-MTKL50U/dp/B0BK1KS6ZD/ref=sr_1_1?_encoding=UTF8&content-id=amzn1.sym.58c90a12-100b-4a2f-8e15-7c06f1abe2be&dib=eyJ2IjoiMSJ9.LpujZ4uISPUK8sa_6yNGVTLp2_seTR9samDUOPD7O24PE2kANyrymdZzhCoNMjav-k7PVK0mn_QKXISGlU4-YJ7wLZ3X_UjjIIV1rSK-EcTX9pXRa2zFEf5cDwl__f6l9M-V5yKGez5HLcPYneH3Jgu5FZuXfSVN_dNYOBt4iauOm5CkCRmYJqP9vWdg5M-XRIKSLK6DESVRxV-xu8WVLf8vvpyPYosKMGvqCSJJMSPpemn7q-1-cAod0DJ81HcagJdXIOvX8ENamCQc4-HPKuSBEjJbz4QTZzHVpXyufwLbx9C-ooVKjYfP9N1yInzltJhJ2AT2MoC3r29Gahsouc0GsoFyjWPkf7v6DPpXQpA.BUx84e9bm4ynJuxv8GC6znmbnly4lzfePsoZ9E2Z1vY&dib_tag=se&pd_rd_r=ae733db4-9f3a-4bf4-9a26-ece873f37580&pd_rd_w=h2KkW&pd_rd_wg=nPE2T&qid=1742378031&refinements=p_85%3A10440599031&rps=1&s=kitchen&sr=1-1&th=1'
    URL2 = 'https://www.amazon.in/Voltas-Anti-dust-183-Vectra-Elegant/dp/B0BQR2WMHX/ref=sr_1_19?_encoding=UTF8&content-id=amzn1.sym.58c90a12-100b-4a2f-8e15-7c06f1abe2be&dib=eyJ2IjoiMSJ9.LpujZ4uISPUK8sa_6yNGVTLp2_seTR9samDUOPD7O24PE2kANyrymdZzhCoNMjav-k7PVK0mn_QKXISGlU4-YJ7wLZ3X_UjjIIV1rSK-EcTX9pXRa2zFEf5cDwl__f6l9M-V5yKGez5HLcPYneH3Jgu5FZuXfSVN_dNYOBt4iauOm5CkCRmYJqP9vWdg5M-XRIKSLK6DESVRxV-xu8WVLf8vvpyPYosKMGvqCSJJMSPpemn7q-1-cAod0DJ81HcagJdXIOvX8ENamCQc4-HPKuSBEjJbz4QTZzHVpXyufwLbx9C-ooVKjYfP9N1yInzltJhJ2AT2MoC3r29Gahsouc0GsoFyjWPkf7v6DPpXQpA.BUx84e9bm4ynJuxv8GC6znmbnly4lzfePsoZ9E2Z1vY&dib_tag=se&pd_rd_r=ae733db4-9f3a-4bf4-9a26-ece873f37580&pd_rd_w=h2KkW&pd_rd_wg=nPE2T&qid=1742378031&refinements=p_85%3A10440599031&rps=1&s=kitchen&sr=1-19#customerReviews'
    compare_products_gemini(URL1, URL2, API_KEY)