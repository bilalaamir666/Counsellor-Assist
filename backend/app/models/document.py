from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


DocumentStatus = Literal[
    "pending",
    "processing",
    "ready",
    "failed"
]


class Document(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    original_filename: str = Field(..., min_length=1, max_length=255)
    file_type: Literal["pdf", "markdown"]
    status: DocumentStatus = "pending"
    failure_reason: Optional[str] = None
    uploaded_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_type: Literal["pdf", "markdown"]
    status: DocumentStatus
    failure_reason: Optional[str] = None
    uploaded_by: str
    created_at: datetime
    updated_at: datetime
