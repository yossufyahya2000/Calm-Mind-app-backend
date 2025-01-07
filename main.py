from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn
import json
from typing import Dict
from dotenv import load_dotenv
import logging
import stripe
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

# Stripe configuration
stripe.api_key = "sk_test_51PTVnz04D1fiiyEWi8oObpVPpEflWz5sOlUreTqQJkfcuNc4j3tcxGVjOYOzt8cWoHrUtvdGOGifZt7JYhpYNRHZ00VSXaa4nB"

from pydantic import BaseModel

class PaymentIntentRequest(BaseModel):
    amount: int
    currency: str = "usd"

@app.post("/create-payment-intent")
async def create_payment_intent(payment_data: PaymentIntentRequest):
    try:
        intent = stripe.PaymentIntent.create(
            amount=payment_data.amount,
            currency=payment_data.currency,
        )
        return {"client_secret": intent.client_secret}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

from pydantic import BaseModel
    
class CreatePaymentSessionRequest(BaseModel):
    amount: int  # Amount in cents
    currency: str  # Currency code (e.g., "usd")
    success_url: str  # URL to redirect after successful payment
    cancel_url: str  # URL to redirect after canceled payment

@app.post("/create-payment-session")
async def create_payment_session(request: CreatePaymentSessionRequest):
    try:
        # Create a Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": request.currency,
                        "product_data": {
                            "name": "Sample Product",  # Replace with your product name
                        },
                        "unit_amount": request.amount,  # Amount in cents
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=request.success_url,
            cancel_url=request.cancel_url,
        )
        return {"session_id": session.id, "url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    
    
    