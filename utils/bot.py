import os
import pinecone
from transformers import AutoModel, AutoTokenizer
from groq import Groq
from dotenv import load_dotenv
import random
import sys

load_dotenv()

def store_chatbot_config(config):
    id = random.randrange(10000000, 99999999)
    chatbot_id = str(id)
    return chatbot_id

# Pinecone initialization
pinecone_api_key = os.getenv('PINECONE_API_KEY')
pinecone_environment = os.getenv('PINECONE_ENVIRONMENT')

pc = pinecone.Pinecone(api_key=pinecone_api_key)
pinecone_index_name = 'index'

if pinecone_index_name not in pc.list_indexes().names():
    pc.create_index(
        name=pinecone_index_name,
        dimension=786,
        metric='cosine',
        spec=pinecone.ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )
pinecone_index = pc.Index(pinecone_index_name)

# Initialize embedding model
model_name = 'jinaai/jina-embeddings-v2-base-en'
revision = 'specific-revision-or-commit-hash'

embedding_model = AutoModel.from_pretrained(model_name, revision=revision, trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(model_name, revision=revision, trust_remote_code=True)

def create_rag_bot(data, model):
    for item in data:
        content = item['content']
        inputs = tokenizer(content, return_tensors='pt', truncation=True, padding=True)
        query_embeddings = embedding_model(**inputs).last_hidden_state.mean(dim=1).detach().numpy().tolist()

        # Generate a unique ID for each piece of content
        content_id = f"content_{hash(content) % ((sys.maxsize + 1) * 2)}"
        pinecone_index.upsert(vectors=[(content_id, query_embeddings[0], {'text': content})])

    print(f"RAG bot created with model: {model}")

def interact_with_rag_bot(user_query, model):
    # Convert user query to vector
    inputs = tokenizer(user_query, return_tensors='pt', truncation=True, padding=True)
    query_embeddings = embedding_model(**inputs).last_hidden_state.mean(dim=1).detach().numpy().tolist()

    # Query the Pinecone index
    result = pinecone_index.query(vector=query_embeddings[0], top_k=5, include_metadata=True)
    matched_info = ' '.join(item['metadata']['text'] for item in result['matches'])
    sources = [item['metadata'].get('source', 'unknown') for item in result['matches']]
    context = f"Information: {matched_info} and the sources: {sources}"
    
    # Create the system prompt
    sys_prompt = f"""
    Instructions:
    - Be helpful and answer questions concisely. If you don't know the answer, say 'I don't know'
    - Utilize the context provided for accurate and specific information.
    - Incorporate your preexisting knowledge to enhance the depth and relevance of your response.
    - Cite your sources
    Context: {context}
    """

    # Initialize the Groq client
    groq_api_key = os.getenv('GROQ_API_KEY')
    client = Groq(api_key=groq_api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_query}
        ]
    )

    return response['choices'][0].message['content']
