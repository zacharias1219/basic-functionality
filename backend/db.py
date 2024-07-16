import pymongo
from pymongo import MongoClient
import chromadb

# MongoDB Client
client = MongoClient('localhost', 27017)
db = client.chatbot_database

# Chroma Client
chroma_client = chromadb.Client()

def initialize_collection():
    try:
        chroma_client.create_collection(name="documents")
    except chromadb.db.base.UniqueConstraintError:
        pass  # Collection already exists
    except ValueError:
        pass  # Collection already exists in another way

initialize_collection()

collection = chroma_client.get_collection(name="documents")
