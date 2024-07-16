import streamlit as st
import requests

# Page setup
st.set_page_config(page_title="Test Your Chatbot", page_icon="🤖", layout="wide")

# Inputs for testing the bot
st.title("Test Your Configured Chatbot")
chatbot_id = st.text_input("Enter your Chatbot ID")
user_input = st.text_area("Ask your chatbot a question")

if st.button('Get Response'):
    response = requests.post(f'http://localhost:8000/api/interact_chatbot/{chatbot_id}', json={"query": user_input})
    if response.status_code == 200:
        st.write("Chatbot Response:")
        st.write(response.json()['response'])
    else:
        st.error("Failed to get response from chatbot.")
