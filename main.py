from fastapi import FastAPI
import uvicorn
from typing import Dict
from dotenv import load_dotenv
import logging
from app.chat.chat import ChatService
from app.chat.message import conversationCreate


load_dotenv()
#
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()



@app.post("/chat")
async def chat_endpoint(message: conversationCreate) -> Dict:
    chat_service = ChatService()
    return await chat_service.process_chat(
        conversation=message
    )
    
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

