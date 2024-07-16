import streamlit as st
import requests
import yaml
from utils.parser import parse_pdf, parse_word, parse_website
from utils.bot import store_chatbot_config
from utils.mail import send_verification_email

# Page setup
st.set_page_config(page_title="Autoserve", page_icon="🤖", layout="centered", initial_sidebar_state="collapsed")

# Initialize session state for knowledge base and integrations
if 'knowledge_base' not in st.session_state:
    st.session_state['knowledge_base'] = []

if 'integrations' not in st.session_state:
    st.session_state['integrations'] = {
        'hubspot': '',
        'mailchimp': '',
        'salesforce': ''
    }

# Inputs from the user
st.title("Create Your AI-Powered Chatbot")
name = st.text_input("Name")
email = st.text_input("Email")

# File upload section
st.header("Upload Files to Knowledge Base")
kb_file = st.file_uploader("Upload File", type=["pdf", "docx", "txt"])

if st.button("Add File to Knowledge Base"):
    if kb_file:
        if kb_file.type == "application/pdf":
            content = parse_pdf(kb_file)
        elif kb_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            content = parse_word(kb_file)
        else:
            st.error("Unsupported file type.")
            st.stop()

        st.session_state['knowledge_base'].append({"format": kb_file.type, "content": content})
        st.success("Added file to Knowledge Base")

# URL section
st.header("Add URLs to Knowledge Base")
kb_url = st.text_input("Enter URL")

if st.button("Add URL to Knowledge Base"):
    if kb_url:
        content = parse_website(kb_url)
        st.session_state['knowledge_base'].append({"name": kb_url, "content": content})
        st.success("Added URL to Knowledge Base")


# Model configuration
st.header("Configure Your Chatbot")
model = st.selectbox("Choose AI Model", ["llama3", "gemma2" , "qwen2", "mistral"])
language = st.selectbox("Language", ["English", "French", "German", "Spanish"])
tone = st.selectbox("Tone", ["Friendly", "Professional", "Casual"])

# Integration selection
st.header("Integration Configuration")
integration_type = st.selectbox("Integration Type", ["HubSpot", "MailChimp", "Salesforce"])

if integration_type == "HubSpot":
    st.session_state['integrations']['hubspot'] = st.text_input("HubSpot User ID", st.session_state['integrations']['hubspot'])
elif integration_type == "MailChimp":
    st.session_state['integrations']['mailchimp'] = st.text_input("MailChimp User ID", st.session_state['integrations']['mailchimp'])
elif integration_type == "Salesforce":
    st.session_state['integrations']['salesforce'] = st.text_input("Salesforce User ID", st.session_state['integrations']['salesforce'])

# Submit button
if st.button('Submit'):
    settings = {
        "language": language.lower(),
        "tone": tone.lower()
    }

    integrations = {
        "hubspot": {"user_id": st.session_state['integrations']['hubspot']},
        "mailchimp": {"user_id": st.session_state['integrations']['mailchimp']},
        "salesforce": {"user_id": st.session_state['integrations']['salesforce']}
    }

    chatbot_config = {
        "name": name,
        "email": email,
        "knowledge_base": st.session_state['knowledge_base'],
        "model": model,
        "settings": settings,
        "integrations": integrations
    }
    
    st.write("Your chatbot configuration:")
    st.json(chatbot_config)

    # Save configuration to YAML
    with open('details.yaml', 'w') as file:
        yaml.dump(chatbot_config, file)
    
    st.write("You can add more files/URLs or change any configuration.")
    if st.button('Verify and Submit'):
        chatbot_id = store_chatbot_config(chatbot_config)
        st.write(f"Chatbot created with ID: {chatbot_id}")

        # Sending verification email
        send_verification_email(name, email, chatbot_id)
        st.success(f"Verification email sent to {email}.")
        # Storing the parameters
        response = requests.post('http://localhost:8000/api/create_chatbot', json=chatbot_config)
        if response.status_code == 200:
            st.success("Chatbot configuration submitted successfully!")
            st.write("A verification email has been sent to you.")
        else:
            st.error("Failed to submit chatbot configuration.")
