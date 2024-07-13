# services/embedding_service.py
from langchain.embeddings import OpenAIEmbeddings

def embed_text(text):
    embedding = OpenAIEmbeddings()
    return embedding.embed_text(text)
