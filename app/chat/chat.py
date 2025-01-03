from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException
from app.chat.message import Message, MessageCreate,conversationCreate
from app.setup.supabaseClinet import supabaseClient
from app.setup.geminiClient import geminiClient
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.supabase = supabaseClient()
        self.model = geminiClient()

    async def create_conversation(self, profile_id: UUID, title: str) -> UUID:
        """Create a new conversation and return its ID."""
        try:
            result = self.supabase.table("conversations").insert({
                "profile_id": str(profile_id),
                "title": title[:50]  # Limit title length
            }).execute()
            return result.data[0]['id']
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            raise HTTPException(status_code=500, detail="Failed to create conversation")

    async def save_message(self, message: MessageCreate) -> Message:
        """Save a message to the database."""
        try:
            result = self.supabase.table("messages").insert({
                "conversation_id": str(message.conversation_id),
                "role": message.role,
                "content": message.content
            }).execute()
            return Message(**result.data[0])
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            raise HTTPException(status_code=500, detail="Failed to save message")

    async def generate_ai_response(self, conversation_id: UUID, user_message: str):
        try:
            # Get conversation history
            history = await self.get_conversation_history(conversation_id)
        
            system_prompt = """You are a supportive and empathetic mental health assistant. 
            Your role is to provide emotional support, active listening, and helpful guidance 
            while maintaining professional boundaries. Never provide medical advice or diagnosis. 
            Focus on empathy, coping strategies, and encouraging professional help when needed."""
        
            conversation_context = "\n".join([
                f"{'User' if msg.role == 'user' else 'Assistant'}: {msg.content}"
                for msg in history
            ])
        
            full_prompt = f"\nConversation history:\n{conversation_context}\n\n User: {user_message}"
            response = self.model.generate_content(full_prompt, stream=True)
            # Return the streaming response directly
            return response
        
        except Exception as e:
            logger.error(f"Failed to generate AI response: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate AI response")

            
            
        
        
    async def process_chat(self, conversation: conversationCreate):
        """Process a chat message and return the streaming AI response."""
        try:
            # Use existing conversation or create new one
            conversation_id = conversation.conversation_id
            if not conversation_id:
                conversation_id = await self.create_conversation(conversation.profile_id, conversation.content)

            # Save user message
            await self.save_message(MessageCreate(
                conversation_id=conversation_id,
                role="user",
                content=conversation.content
            ))

            # Generate streaming response
            response_stream = await self.generate_ai_response(conversation_id, conversation.content)
            
            # Return both the stream and conversation_id
            return {
                    "stream": response_stream,
                    "conversation_id": conversation_id
                }

        except Exception as e:
            logger.error(f"Chat processing error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_conversation_history(self, conversation_id: UUID) -> List[Message]:
        """Retrieve message history for a conversation."""
        try:
            result = self.supabase.table("messages")\
                .select("*")\
                .eq("conversation_id", str(conversation_id))\
                .order("created_at")\
                .execute()
            return [Message(**msg) for msg in result.data]
        except Exception as e:
            logger.error(f"Failed to fetch conversation history: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch conversation history")
