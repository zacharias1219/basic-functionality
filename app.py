import streamlit as st
import logging
import os
import tempfile
import shutil
import requests
import yaml
from bs4 import BeautifulSoup
from groq import Groq
from typing import List, Any, Optional, Dict, Tuple
import chardet
import pdfplumber
import nltk

nltk.download('punkt')

from utils.bot import store_chatbot_config
from utils.mail import send_verification_email
from utils.parser import parse_pdf, parse_website

from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.runnables import Runnable, RunnablePassthrough

# Page setup
st.set_page_config(page_title="Autoserve", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

# Initialize session state for knowledge base and integrations
if 'knowledge_base' not in st.session_state:
    st.session_state['knowledge_base'] = []

if 'integrations' not in st.session_state:
    st.session_state['integrations'] = {
        'hubspot': '',
        'mailchimp': '',
        'salesforce': ''
    }

if 'url_text' not in st.session_state:
    st.session_state['url_text'] = ""

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

# Load API key from secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Define model details
models = {
    "gemma-7b-it": {"name": "Gemma-7b-it", "tokens": 8192, "developer": "Google"},
    "llama2-70b-4096": {"name": "LLaMA2-70b-chat", "tokens": 4096, "developer": "Meta"},
    "llama3-70b-8192": {"name": "LLaMA3-70b-8192", "tokens": 8192, "developer": "Meta"},
    "llama3-8b-8192": {"name": "LLaMA3-8b-8192", "tokens": 8192, "developer": "Meta"},
    "mixtral-8x7b-32768": {"name": "Mixtral-8x7b-Instruct-v0.1", "tokens": 32768, "developer": "Mistral"},
}

@st.cache_resource(show_spinner=True)
def extract_model_names(models_info: Dict[str, List[Dict[str, Any]]]) -> Tuple[str, ...]:
    logger.info("Extracting model names from models_info")
    model_names = tuple(model["name"] for model in models_info["models"])
    logger.info(f"Extracted model names: {model_names}")
    return model_names

def create_vector_db(content: str) -> Chroma:
    logger.info("Creating vector DB from content")
    temp_dir = tempfile.mkdtemp()

    try:
        with open(os.path.join(temp_dir, "temp.txt"), "w", encoding='utf-8') as f:
            f.write(content)
            logger.info("Content saved to temporary file")
        
        loader = UnstructuredFileLoader(os.path.join(temp_dir, "temp.txt"))
        data = loader.load()
        logger.info(f"Loaded data: {data}")

        if not data:
            raise ValueError("No data loaded from the file.")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=7500, chunk_overlap=100)
        chunks = text_splitter.split_documents(data)
        logger.info(f"Document split into chunks: {chunks}")

        if not chunks:
            raise ValueError("No chunks created from the document.")

        try:
            embeddings = OllamaEmbeddings(model="nomic-embed-text", show_progress=True)
            vector_db = Chroma.from_documents(
                documents=chunks, embedding=embeddings, collection_name="myRAG"
            )
            logger.info("Vector DB created")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            st.error("Failed to connect to the embedding service. Please ensure it is running and try again.")
            return None
    finally:
        shutil.rmtree(temp_dir)
        logger.info(f"Temporary directory {temp_dir} removed")
    
    return vector_db

class GroqRunnable(Runnable):
    def __init__(self, client: Groq):
        self.client = client

    def invoke(self, *args, **kwargs) -> str:
        input_data = str(args[0])  # Ensure the input data is a string
        response = self.client.chat.completions.create(
            messages=[
                {"role": "user", "content": input_data}
            ],
            model="llama3-8b-8192",  # Use the correct model key
            temperature=0.7,
            max_tokens=256,
            top_p=1
        )
        return response.choices[0].message.content

def process_question(question: str, vector_db: Chroma, selected_model: str) -> str:
    logger.info(f"Processing question: {question} using model: {selected_model}")

    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assistant. Your task is to generate 3
        different versions of the given user question to retrieve relevant documents from
        a vector database. By generating multiple perspectives on the user question, your
        goal is to help the user overcome some of the limitations of the distance-based
        similarity search. Provide these alternative questions separated by newlines.
        Original question: {question}""",
    )

    retriever = MultiQueryRetriever.from_llm(
        vector_db.as_retriever(), GroqRunnable(client), prompt=QUERY_PROMPT
    )

    template = """Answer the question based ONLY on the following context:
    {context}
    Question: {question}
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Only provide the answer from the {context}, nothing else.
    Add snippets of the context you used to answer the question.
    """

    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | GroqRunnable(client)
        | StrOutputParser()
    )

    response = chain.invoke(question)
    logger.info("Question processed and response generated")
    return response

def parse_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get all text content
    text = soup.get_text(separator='\n')

    # Remove excessive gaps
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    cleaned_text = '\n.join(lines)'

    return cleaned_text

def delete_vector_db(vector_db: Optional[Chroma]) -> None:
    logger.info("Deleting vector DB")
    if vector_db is not None:
        vector_db.delete_collection()
        st.session_state.pop("url_text", None)
        st.session_state.pop("file_upload", None)
        st.session_state.pop("vector_db", None)
        st.success("Collection and temporary files deleted successfully.")
        logger.info("Vector DB and related session state cleared")
        st.rerun()
    else:
        st.error("No vector database found to delete.")
        logger.warning("Attempted to delete vector DB, but none was found")

def main() -> None:
    st.header("🧠 Auto Serve", anchor=False)
    st.subheader("Automate your chatbot creation. Test the models first to see which one you like.", divider="rainbow")
    input1, input2 = st.columns([1.5, 2])
    with input1:
        name = st.text_input("Name")
    with input2:
        email = st.text_input("Email")

    st.divider()

    col1, col2 = st.columns([1.5, 2])

    if 'knowledge_base' not in st.session_state:
        st.session_state['knowledge_base'] = []

    if 'integrations' not in st.session_state:
        st.session_state['integrations'] = {
            'hubspot': '',
            'mailchimp': '',
            'salesforce': ''
    }

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if "vector_db" not in st.session_state:
        st.session_state["vector_db"] = None

    if "selected_model" not in st.session_state:
        st.session_state["selected_model"] = None

    if models:
        selected_model = col2.selectbox(
            "Pick a model↓", list(models.keys())
        )
        st.session_state["selected_model"] = selected_model

    with col1:
        file_upload = st.file_uploader("Upload a file ↓", type=["pdf", "txt"], accept_multiple_files=False)
        if file_upload:
            st.session_state["file_upload"] = file_upload
            try:
                if file_upload.type == "application/pdf":
                    content = parse_pdf(file_upload)
                else:
                    raw_content = file_upload.read()
                    encoding = chardet.detect(raw_content)['encoding']
                    content = raw_content.decode(encoding)

                if st.session_state["vector_db"] is None:
                    st.session_state["vector_db"] = create_vector_db(content)
            except UnicodeDecodeError as e:
                st.error(f"Could not decode file using {encoding} encoding.")
                logger.error(f"UnicodeDecodeError: {str(e)}")
                return
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
                logger.error(f"Error processing file: {str(e)}")
                return

        if st.button("Add File to Knowledge Base"):
            if file_upload:
                if file_upload.type == "application/pdf":
                    content = parse_pdf(file_upload)
                else:
                    raw_content = file_upload.read()
                    encoding = chardet.detect(raw_content)['encoding']
                    content = raw_content.decode(encoding)

                st.session_state['knowledge_base'].append({"format": file_upload.type, "content": content})
                st.success("Added file to Knowledge Base")

        url_upload = st.text_input("Enter a URL ↓")

        if st.button("Add URL to Knowledge Base"):
            if url_upload:
                content = parse_website(url_upload)
                st.session_state['knowledge_base'].append({"name": url_upload, "content": content})
                st.session_state['url_text'] += content + "\n"
                if st.session_state["vector_db"] is None:
                    st.session_state["vector_db"] = create_vector_db(st.session_state['url_text'])
                st.success("Added URL to Knowledge Base")

        delete_collection = col1.button("⚠️ Delete collection", type="secondary")

        if delete_collection:
            delete_vector_db(st.session_state["vector_db"])

    with col2:
        message_container = st.container(height=500, border=True)

        for message in st.session_state["messages"]:
            avatar = "🤖" if message["role"] == "assistant" else "😎"
            with message_container.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

        if prompt := st.chat_input("Enter a prompt here..."):
            try:
                st.session_state["messages"].append({"role": "user", "content": prompt})
                message_container.chat_message("user", avatar="😎").markdown(prompt)

                with message_container.chat_message("assistant", avatar="🤖"):
                    with st.spinner(":green[processing...]"):
                        if st.session_state["vector_db"] is not None:
                            response = process_question(
                                prompt, st.session_state["vector_db"], st.session_state["selected_model"]
                            )
                            st.markdown(response)
                        else:
                            st.warning("Please upload a file or add a URL first.")

                if st.session_state["vector_db"] is not None:
                    st.session_state["messages"].append({"role": "assistant", "content": response})

            except Exception as e:
                st.error(e, icon="⛔️")
                logger.error(f"Error processing prompt: {e}")

    if st.session_state["vector_db"] is None:
        st.warning("Upload a file or add a URL to begin chat...")

    st.divider()

    # Configuration for integrations
    st.subheader("Configure Your Chatbot")
    language = st.selectbox("Language", ["English", "French", "German", "Spanish"])
    tone = st.selectbox("Tone", ["Friendly", "Professional", "Casual"])

    st.subheader("Integration Configuration")
    integration_type = st.selectbox("Integration Type", ["HubSpot", "MailChimp", "Salesforce"])

    if integration_type == "HubSpot":
        st.session_state['integrations']['hubspot'] = st.text_input("HubSpot User ID", st.session_state['integrations']['hubspot'])
    elif integration_type == "MailChimp":
        st.session_state['integrations']['mailchimp'] = st.text_input("MailChimp User ID", st.session_state['integrations']['mailchimp'])
    elif integration_type == "Salesforce":
        st.session_state['integrations']['salesforce'] = st.text_input("Salesforce User ID", st.session_state['integrations']['salesforce'])

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
            "model": selected_model,
            "settings": settings,
            "integrations": integrations
        }

        st.write("Your chatbot configuration:")
        st.json(chatbot_config)

        # Save configuration to YAML
        with open('details.yaml', 'w') as file:
            yaml.dump(chatbot_config, file)

        st.write("You can add more files/URLs or change any configuration.")
        chatbot_id = store_chatbot_config(chatbot_config)
        st.write(f"Chatbot created with ID: {chatbot_id}")

        if st.button('Verify and Submit'):
            # Storing the parameters
            response = requests.post('http://localhost:8000/api/create_chatbot', json=chatbot_config)
            if response.status_code == 200:
                st.success("Chatbot configuration submitted successfully!")
                st.write("A verification email has been sent to you.")
            else:
                st.error("Failed to submit chatbot configuration.")

        # Sending verification email
        mail_status = send_verification_email(name, email, chatbot_id)
        st.success(mail_status)


if __name__ == "__main__":
    main()
