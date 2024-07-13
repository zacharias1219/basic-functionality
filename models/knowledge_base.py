# models/knowledge_base.py
from weaviate import Client as WeaviateClient
from weaviate.util import generate_uuid5

from config import WEAVIATE_URL

client = WeaviateClient(WEAVIATE_URL)

def index_document(content, class_name="KnowledgeBase"):
    doc_id = generate_uuid5(content)
    client.batch.add_data_object({"content": content}, class_name, doc_id)

def retrieve_documents(query, class_name="KnowledgeBase"):
    response = client.query.get(class_name, ["content"]).with_near_text({"concepts": [query]}).do()
    return [doc["content"] for doc in response["data"]["Get"][class_name]]
