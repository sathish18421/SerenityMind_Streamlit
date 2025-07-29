import requests

API_URLS = {
    "sentiment": "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment",
    "emotion": "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base",
    "motivator": "https://api-inference.huggingface.co/models/gpt2"
}

HEADERS = {
    "Authorization": "Bearer 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"
}

def query_huggingface_api(payload, url_key):
    response = requests.post(API_URLS[url_key], headers=HEADERS, json={"inputs": payload})
    try:
        return response.json()
    except:
        return {"error": "Failed to parse API response"}
