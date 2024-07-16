from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bot import create_chatbot, interact_with_chatbot
from mail import send_verification_email

app = FastAPI()

class ChatbotConfig(BaseModel):
    name: str
    email: str
    knowledge_base: dict
    model: str
    settings: dict
    integrations: dict
    knowledge_base: list

@app.post("/api/create_chatbot")
async def create_chatbot_endpoint(config: ChatbotConfig):
    chatbot_id = create_chatbot(config)
    send_verification_email(config.name, config.email, chatbot_id)
    return {"chatbot_id": chatbot_id}

@app.post("/api/interact_chatbot/{chatbot_id}")
async def interact_chatbot_endpoint(chatbot_id: str, query: dict):
    try:
        response = interact_with_chatbot(chatbot_id, query['query'])
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
