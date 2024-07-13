# services/ollama_service.py
import requests
from config import OLLAMA_API_KEY

def generate_response(model, prompt, context):
    headers = {
        'Authorization': f'Bearer {OLLAMA_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        "model": model,
        "prompt": prompt,
        "context": context
    }

    response = requests.post("https://api.ollama.ai/v1/generate", json=payload, headers=headers)
    response_data = response.json()
    return response_data['text']
