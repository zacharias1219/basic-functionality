import streamlit as st
import json
import requests
from backend.utils.parser import parse_pdf, parse_word, parse_website

# Initialize Chroma client
import chromadb
client = chromadb.Client()
collection = client.create_collection(name="documents")

# Streamlit App
st.title("AI-Powered Chatbot Creator")

# Knowledge Base Management
st.header("Manage Knowledge Base")

# File upload section
st.subheader("Upload Files to Knowledge Base")
kb_file = st.file_uploader("Upload File", type=["pdf", "docx"])

if st.button("Add File to Knowledge Base"):
    if kb_file:
        if kb_file.type == "application/pdf":
            content = parse_pdf(kb_file)
        elif kb_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            content = parse_word(kb_file)
        else:
            st.error("Unsupported file type.")
            st.stop()

        doc_id = f"doc_{len(st.session_state.get('knowledge_base', [])) + 1}"
        embedding = [0.1, 0.2, 0.3]  # Replace with actual embedding generation
        metadata = {"title": kb_file.name, "content": content, "format": kb_file.type}
        
        collection.add({"id": doc_id, "embedding": embedding, "metadata": metadata})
        
        st.session_state['knowledge_base'] = st.session_state.get('knowledge_base', []) + [{"id": doc_id, "embedding": embedding, "metadata": metadata}]
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
email_id = st.text_input("Email:")

# AI model selection
model = st.selectbox("Choose AI Model", ["llama3", "mistral", "gemma7b", "starling"])

# Language selection
language = st.selectbox("Language", ["English", "French", "German", "Spanish", "Chinese", "Japanese"])

# Tone selection
tone = st.selectbox("Tone", ["Friendly", "Professional", "Casual"])

# Integration selection
integration_type = st.selectbox("Integration Type", ["HubSpot", "MailChimp", "Salesforce"])

if integration_type == "HubSpot":
    st.session_state['integrations']['hubspot'] = st.text_input("HubSpot User ID", st.session_state['integrations']['hubspot'])
elif integration_type == "MailChimp":
    st.session_state['integrations']['mailchimp'] = st.text_input("MailChimp User ID", st.session_state['integrations']['mailchimp'])
elif integration_type == "Salesforce":
    st.session_state['integrations']['salesforce'] = st.text_input("Salesforce User ID", st.session_state['integrations']['salesforce'])

if st.button("Create Chatbot"):
    settings = {
        "language": language.lower(),
        "tone": tone.lower()
    }

    integrations = {
        "hubspot": {"user_id": st.session_state['integrations']['hubspot']},
        "mailchimp": {"user_id": st.session_state['integrations']['mailchimp']},
        "salesforce": {"user_id": st.session_state['integrations']['salesforce']}
    }

    chatbot_data = {
        "email": email_id,
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
    response = requests.post('http://localhost:8000/api/create_chatbot', json=chatbot_data)
    
    if response.status_code == 200:
        st.success("Chatbot successfully created on the server!")
        chatbot_id = response.json().get("chatbot_id")
        code_snippet = f'<iframe src="https://yourserver.com/chatbot?chatbot_id={chatbot_id}" width="300" height="500"></iframe>'
        st.code(code_snippet, language='html')
    else:
        st.error(f"Failed to create chatbot on the server: {response.text}")
