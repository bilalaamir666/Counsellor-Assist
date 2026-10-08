from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_type: str
    status: str
