from datetime import datetime

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    document_id: str
    content: str = Field(..., min_length=1)
    page_number: int = Field(..., ge=1)
    chunk_index: int = Field(..., ge=0)
    embedding: list[float] | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
