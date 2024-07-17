import streamlit as st
from utils.bot import interact_with_rag_bot
import yaml

# Load configuration
with open('details.yaml', 'r') as file:
    chatbot_config = yaml.safe_load(file)

# Page setup
st.set_page_config(page_title="Test Your Chatbot", page_icon="🤖", layout="wide")

# Inputs for testing the bot
st.title("Test Your Configured Chatbot")

user_query = st.text_input("Enter your question")
model_name = chatbot_config['model']

if st.button("Submit"):
    try:
        response = interact_with_rag_bot(user_query, model_name)
        st.write(response)
    except Exception as e:
        st.error(f"Error interacting with RAG bot: {e}")
