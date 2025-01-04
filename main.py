from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn
import json
from typing import Dict
from dotenv import load_dotenv
import logging
from app.chat.chat import ChatService
from app.chat.message import conversationCreate,MessageCreate


load_dotenv()
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/chat")
async def chat_endpoint(message: conversationCreate):
    chat_service = ChatService()
    
    async def generate():
        response = await chat_service.process_chat(conversation=message)
        conversation_id = response["conversation_id"]
        
        # Send conversation_id first
        #yield f"data: {json.dumps({'conversation_id': str(conversation_id)})}\n\n"
        full_response = ""
        streamResponse = response["stream"]
        # Handle streaming response properly
        for chunk in streamResponse:
            if chunk.text:
                full_response += chunk.text
                yield f"data: {json.dumps({'text': chunk.text,'conversation_id': str(conversation_id)})}\n\n"
                
        # Save user message
        await chat_service.save_message(MessageCreate(
            conversation_id=conversation_id,
            role="user",
            content=message.content
        ))
          
        # Save ass message  
        await chat_service.save_message(MessageCreate(
            conversation_id=conversation_id,
            role="assistant",
            content=full_response
        ))

    return StreamingResponse(generate(), media_type="text/event-stream")

#
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    
    