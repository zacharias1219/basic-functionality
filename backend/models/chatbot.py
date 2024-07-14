from pydantic import BaseModel
from typing import List, Dict, Any

class ChatbotConfig(BaseModel):
    email: str
    model: str
    settings: Dict[str, Any]
    integrations: Dict[str, Dict[str, str]]
    knowledge_base: List[Dict[str, Any]]
