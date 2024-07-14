from backend.db import add_document_to_chroma, query_chroma

def index_document(doc_id, embedding, metadata):
    add_document_to_chroma(doc_id, embedding, metadata)

def retrieve_documents(query_embedding, top_k=5):
    return query_chroma(query_embedding, top_k)