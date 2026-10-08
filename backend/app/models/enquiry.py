from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


EnquiryStatus = Literal[
    "new",
    "contacted",
    "documents pending",
    "applied",
    "visa in process",
    "closed"
]


class Note(BaseModel):
    author_id: str
    content: str = Field(..., min_length=1, max_length=2000)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StatusChange(BaseModel):
    status: EnquiryStatus
    changed_by: str
    changed_at: datetime = Field(default_factory=datetime.utcnow)


class Enquiry(BaseModel):
    student_name: str = Field(..., min_length=2, max_length=100)
    student_email: EmailStr
    student_phone: str = Field(..., min_length=5, max_length=30)
    nationality: str = Field(..., min_length=2, max_length=100)

    course: str = Field(..., min_length=1, max_length=200)
    intake: str = Field(..., min_length=1, max_length=100)

    status: EnquiryStatus = "new"

    assigned_counsellor: Optional[str] = None

    notes: list[Note] = Field(default_factory=list)
    status_history: list[StatusChange] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EnquiryResponse(BaseModel):
    id: str
    student_name: str
    student_email: EmailStr
    student_phone: str
    nationality: str
    course: str
    intake: str
    status: EnquiryStatus
    assigned_counsellor: Optional[str]
    notes: list[Note]
    status_history: list[StatusChange]
    created_at: datetime
    updated_at: datetime
