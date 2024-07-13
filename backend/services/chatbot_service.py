from db import db
from models.chatbot import ChatbotConfig
from models.knowledge_base import index_document, retrieve_documents
from services.ollama_service import generate_response
from services.embedding_service import embed_text
from services.integrators.hubspot_service import sync_hubspot
from services.integrators.mailchimp_service import sync_mailchimp
from services.integrators.salesforce_service import sync_salesforce

def create_chatbot(config: ChatbotConfig):
    config_dict = config.dict()
    result = db.chatbots.insert_one(config_dict)
    
    for item in config.knowledge_base:
        content = item['content']
        index_document(content)

    return {"chatbot_id": str(result.inserted_id)}

def interact_with_chatbot(chatbot_id, user_query):
    chatbot = db.chatbots.find_one({"_id": chatbot_id})
    if not chatbot:
        raise ValueError("Chatbot not found")

    documents = retrieve_documents(user_query)
    response = generate_response(chatbot['model'], user_query, documents)
    return response

def handle_integrations(integrations, data):
    if 'hubspot' in integrations:
        sync_hubspot(integrations['hubspot']['api_key'], data)
    if 'mailchimp' in integrations:
        sync_mailchimp(integrations['mailchimp']['api_key'], integrations['mailchimp']['list_id'], data)
    if 'salesforce' in integrations:
        sync_salesforce(integrations['salesforce']['api_key'], integrations['salesforce']['instance_url'], data)
