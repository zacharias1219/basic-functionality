import os
from groq import Groq
from dotenv import load_dotenv
import random

load_dotenv()

def store_chatbot_config(config):
    id = random.randrange(10000000,99999999)
    chatbot_id = str(id)
    return chatbot_id

def get_chatbot_config(chatbot_id):
    # Retrieve the bot configuration from a file or database
    return {
        "name": "Example Bot",
        "model": "gemma2",
        "settings": {"language": "english", "tone": "friendly"},
        "integrations": {},
        "knowledge_base": {}
    }

def create_chatbot(config):
    # Initialize the Groq client
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))

    # Store the bot configuration
    chatbot_id = store_chatbot_config(config)
    return chatbot_id

def interact_with_chatbot(chatbot_id, user_query):
    config = get_chatbot_config(chatbot_id)
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    response = client.chat.create(
        model=config['model'],
        messages=[{"role": "user", "content": user_query}]
    )
    return response['choices'][0]['text']
