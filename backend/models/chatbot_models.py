"""
Pydantic models for chatbot API validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict


class ChatMessageRequest(BaseModel):
    """Request model for sending chat message."""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    context: Optional[Dict] = Field(None, description="Optional context (pricing data, market info)")


class ChatClearRequest(BaseModel):
    """Request model for clearing chat history."""
    pass
