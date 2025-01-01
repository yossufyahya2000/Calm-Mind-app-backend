from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from dotenv import load_dotenv
import logging
from pathlib import Path
from app.chat.chat import ChatService
from app.chat.message import conversationCreate


load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

#

@app.post("/chat")
async def chat_endpoint(message: conversationCreate) -> Dict:
    chat_service = ChatService()
    return await chat_service.process_chat(
        conversation=message
    )


