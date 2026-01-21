"""
Pydantic models for chat session management.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class ChatMessage(BaseModel):
    """Individual chat message model."""
    role: Literal['user', 'assistant', 'system'] = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")
    tokens_used: Optional[int] = Field(None, description="Tokens used for this message (assistant only)")


class ChatSession(BaseModel):
    """Chat session model."""
    id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    title: Optional[str] = Field(None, description="Session title (auto-generated from first message)")
    messages: List[ChatMessage] = Field(default_factory=list, description="Chat messages")
    total_tokens: int = Field(default=0, description="Total tokens used in session")
    created_at: datetime = Field(..., description="Session creation time")
    updated_at: datetime = Field(..., description="Last update time")
    is_active: bool = Field(default=True, description="Whether session is currently active")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "chat_1234567890",
                "user_id": "user_123",
                "title": "Options pricing discussion",
                "messages": [
                    {
                        "role": "user",
                        "content": "What is Black-76 model?",
                        "timestamp": "2026-01-20T14:30:25"
                    },
                    {
                        "role": "assistant",
                        "content": "Black-76 is an options pricing model...",
                        "timestamp": "2026-01-20T14:30:27",
                        "tokens_used": 150
                    }
                ],
                "total_tokens": 150,
                "created_at": "2026-01-20T14:30:25",
                "updated_at": "2026-01-20T14:30:27",
                "is_active": True
            }
        }


class ChatSessionListResponse(BaseModel):
    """Response model for list of chat sessions."""
    sessions: List[ChatSession]
    total: int = Field(..., description="Total number of sessions")
    page: int = Field(default=1, description="Current page number")
    per_page: int = Field(default=20, description="Sessions per page")
