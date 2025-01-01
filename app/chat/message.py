from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class MessageBase(BaseModel):
    role: str = "user"
    content: str

class MessageCreate(MessageBase):
    conversation_id: UUID  
    
class conversationCreate(MessageBase):
    profile_id: UUID  
    conversation_id: UUID | None = None 
    
class Message(MessageBase):
    id: UUID
    conversation_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True