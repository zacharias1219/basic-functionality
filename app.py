import streamlit as st
import openai
import json
import requests
from ai import generate_response
from utils.parser import parse_pdf, parse_word, parse_image, parse_website

# Set your OpenAI API key
openai.api_key = 'YOUR_OPENAI_API_KEY'

# Initialize session state for integrations
if 'integrations' not in st.session_state:
    st.session_state['integrations'] = {
        'hubspot': '',
        'mailchimp': '',
        'salesforce': ''
    }

# Initialize session state for knowledge base
if 'knowledge_base' not in st.session_state:
    st.session_state['knowledge_base'] = []

# Streamlit App
st.title("AI-Powered Chatbot Creator")

# Knowledge Base Management
st.header("Manage Knowledge Base")

# File upload section
st.subheader("Upload Files to Knowledge Base")
kb_file = st.file_uploader("Upload File", type=["pdf", "docx", "jpg", "jpeg", "png"])

if st.button("Add File to Knowledge Base"):
    if kb_file:
        if kb_file.type == "application/pdf":
            content = parse_pdf(kb_file)
        elif kb_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            content = parse_word(kb_file)
        elif kb_file.type in ["image/jpeg", "image/png"]:
            content = parse_image(kb_file)
        else:
            st.error("Unsupported file type.")
            st.stop()

        st.session_state['knowledge_base'].append({"format": kb_file.type, "content": content})
        st.success("Added file to Knowledge Base")

# URL section
st.subheader("Add URLs to Knowledge Base")
kb_url = st.text_input("Enter URL")

if st.button("Add URL to Knowledge Base"):
    if kb_url:
        content = parse_website(kb_url)
        st.session_state['knowledge_base'].append({"format": "url", "content": content})
        st.success("Added URL to Knowledge Base")

# Display knowledge base entries
st.subheader("Knowledge Base Entries")

for item in st.session_state['knowledge_base']:
    st.write(f"**Format:** {item['format']}")
    st.write(f"**Content:** {item['content'][:500]}...")  # Displaying first 500 characters for brevity
    st.write("---")

# Chatbot Creation
st.header("Create Your AI-Powered Chatbot")

# User inputs
user_id = st.text_input("User ID")

# AI model selection
model = st.selectbox("Choose AI Model", ["gpt-3.5-turbo", "gpt-4", "claude", "opus", "gemini", "llama-3"])

# Language selection
language = st.selectbox("Language", ["English", "French", "German", "Spanish", "Chinese", "Japanese"])

# Tone selection
tone = st.selectbox("Tone", ["Friendly", "Professional", "Casual"])

# Integration selection
integration_type = st.selectbox("Integration Type", ["HubSpot", "MailChimp", "Salesforce"])

if integration_type == "HubSpot":
    st.session_state['integrations']['hubspot'] = st.text_input("HubSpot API Key", st.session_state['integrations']['hubspot'])
elif integration_type == "MailChimp":
    st.session_state['integrations']['mailchimp'] = st.text_input("MailChimp API Key", st.session_state['integrations']['mailchimp'])
elif integration_type == "Salesforce":
    st.session_state['integrations']['salesforce'] = st.text_input("Salesforce API Key", st.session_state['integrations']['salesforce'])

if st.button("Create Chatbot"):
    settings = {
        "language": language.lower(),
        "tone": tone.lower()
    }

    integrations = {
        "hubspot": {"api_key": st.session_state['integrations']['hubspot']},
        "mailchimp": {"api_key": st.session_state['integrations']['mailchimp']},
        "salesforce": {"api_key": st.session_state['integrations']['salesforce']}
    }

    chatbot_data = {
        "user_id": user_id,
        "model": model,
        "settings": settings,
        "integrations": integrations,
        "knowledge_base": st.session_state['knowledge_base']
    }
    
    # Convert chatbot data to JSON
    chatbot_json = json.dumps(chatbot_data, indent=4)
    
    # Display JSON
    st.success("Chatbot created successfully!")
    st.json(chatbot_json)

    # Send JSON data to server
    # Replace 'http://yourserver.com/api/create_chatbot' with your actual backend endpoint
    response = requests.post('http://yourserver.com/api/create_chatbot', json=chatbot_data)
    
    if response.status_code == 200:
        st.success("Chatbot successfully created on the server!")
    else:
        st.error(f"Failed to create chatbot on the server: {response.text}")

# Testing the chatbot
st.header("Test Your Chatbot")

chatbot_id = st.text_input("Chatbot ID for Testing")
prompt = st.text_area("Prompt")

if st.button("Get Response"):
    response = generate_response(prompt, model)
    st.write(response)
