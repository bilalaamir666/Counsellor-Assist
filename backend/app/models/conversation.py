from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


MessageRole = Literal[
    "user",
    "assistant"
]


class Source(BaseModel):
    document_id: str
    document_name: str
    page_number: int
    snippet: str


class Message(BaseModel):
    role: MessageRole
    content: str = Field(..., min_length=1)
    sources: list[Source] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Conversation(BaseModel):
    user_id: str
    messages: list[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    messages: list[Message]
    created_at: datetime
    updated_at: datetime
