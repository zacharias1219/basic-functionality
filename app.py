import streamlit as st
import openai
from pymongo import MongoClient
from ai import generate_response
from models import Chatbot
from integrators import salesforce, hubspot, mailchimp

# Set your OpenAI API key
openai.api_key = 'YOUR_OPENAI_API_KEY'

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db_mongo = client['chatbot_project']
chatbots_collection = db_mongo['chatbots']

# Streamlit App
st.title("AI-Powered Chatbot Creator")

st.header("Create Your AI-Powered Chatbot")

# User inputs
user_id = st.text_input("User ID")
model = st.selectbox("Choose AI Model", ["gpt-3.5-turbo", "gpt-4"])
settings = st.text_area("Chatbot Settings (JSON)", '{"language": "en", "tone": "friendly"}')
integrations = st.text_area("Integrations (JSON)", '{"hubspot": {"api_key": "your_api_key"}}')

if st.button("Create Chatbot"):
    chatbot_data = {
        "user_id": user_id,
        "model": model,
        "settings": settings,
        "integrations": integrations
    }
    
    # Save chatbot to MongoDB
    chatbots_collection.insert_one(chatbot_data)
    
    # Generate code snippet
    chatbot_id = str(chatbot_data['_id'])
    code_snippet = f'<script src="https://yourdomain.com/chatbot.js?chatbot_id={chatbot_id}"></script>'
    st.success("Chatbot created successfully!")
    st.code(code_snippet, language='html')

# Testing the chatbot
st.header("Test Your Chatbot")

chatbot_id = st.text_input("Chatbot ID")
prompt = st.text_area("Prompt")

if st.button("Get Response"):
    # Fetch chatbot settings from MongoDB
    chatbot = chatbots_collection.find_one({"_id": ObjectId(chatbot_id)})
    model = chatbot["model"]
    response = generate_response(prompt, model)
    st.write(response)
