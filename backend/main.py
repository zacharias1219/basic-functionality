from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from bson import ObjectId

from models.chatbot import ChatbotConfig
from services.chatbot_service import create_chatbot, interact_with_chatbot, handle_integrations

app = FastAPI()

@app.post("/api/create_chatbot")
async def create_chatbot_endpoint(config: ChatbotConfig):
    try:
        result = create_chatbot(config)
        handle_integrations(config.integrations, {"email": config.email})
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/chatbot_interact")
async def chatbot_interact_endpoint(request: Request):
    data = await request.json()
    chatbot_id = ObjectId(data['chatbot_id'])
    user_query = data['user_query']
    try:
        response = interact_with_chatbot(chatbot_id, user_query)
        return {"response": response}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
