# models/chatbot.py
from pydantic import BaseModel
from typing import List, Dict

class ChatbotConfig(BaseModel):
    email: str
    model: str
    settings: Dict[str, str]
    integrations: Dict[str, Dict[str, str]]
    knowledge_base: List[Dict[str, str]]
