import pymongo
from pymongo import MongoClient
import chromadb

# MongoDB Client
client = MongoClient('localhost', 27017)
db = client.chatbot_database

# Chroma Client
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="documents")

def add_document_to_chroma(doc_id, embedding, metadata):
    collection.add({"id": doc_id, "embedding": embedding, "metadata": metadata})

def query_chroma(query_embedding, top_k=5):
    results = collection.query(query_embedding=query_embedding, top_k=top_k)
    return results
