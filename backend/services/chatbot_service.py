from db import db
from models.chatbot import ChatbotConfig
from models.knowledge_base import index_document, retrieve_documents
from services.ollama_service import generate_response
from services.embedding_service import embed_text
from services.integrators.hubspot_service import sync_hubspot
from services.integrators.mailchimp_service import sync_mailchimp
from services.integrators.salesforce_service import sync_salesforce
from services.chromadb_service import add_document, search_documents
from bson import ObjectId

def create_chatbot(config: ChatbotConfig):
    config_dict = config.dict()
    result = db.chatbots.insert_one(config_dict)
    
    for item in config.knowledge_base:
        content = item['content']
        embedding = embed_text(content)
        metadata = {"title": item['title'], "format": item['format']}
        add_document(item['id'], embedding, metadata)

    return {"chatbot_id": str(result.inserted_id)}

def interact_with_chatbot(chatbot_id, user_query):
    chatbot = db.chatbots.find_one({"_id": ObjectId(chatbot_id)})
    if not chatbot:
        raise ValueError("Chatbot not found")

    query_embedding = embed_text(user_query)
    documents = search_documents(query_embedding)
    context = " ".join([doc["metadata"]["content"] for doc in documents])
    response = generate_response(chatbot['model'], user_query, context)
    return response

def handle_integrations(integrations, data):
    if 'hubspot' in integrations:
        sync_hubspot(integrations['hubspot']['user_id'], data)
    if 'mailchimp' in integrations:
        sync_mailchimp(integrations['mailchimp']['user_id'], data)
    if 'salesforce' in integrations:
        sync_salesforce(integrations['salesforce']['user_id'], data)
