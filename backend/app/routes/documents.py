import os
import shutil
from datetime import datetime

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status
)

from app.models.document import Document
from app.schemas.document import DocumentUploadResponse
from app.services.document_service import create_document
from app.services.document_processing_service import process_document
from app.utils.auth import require_admin


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


UPLOAD_DIR = "uploads"


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED
)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user=Depends(require_admin)
):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required"
        )

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in [".pdf", ".md"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and Markdown files are allowed"
        )

    file_type = "pdf" if extension == ".pdf" else "markdown"

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    stored_filename = (
        f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        f"{extension}"
    )

    file_path = os.path.join(
        UPLOAD_DIR,
        stored_filename
    )

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        now = datetime.utcnow()

        document = Document(
            filename=stored_filename,
            original_filename=file.filename,
            file_type=file_type,
            status="pending",
            uploaded_by=str(current_user["_id"]),
            created_at=now,
            updated_at=now
        )

        document_id = create_document(
            document.model_dump()
        )

        # Start document processing after the response is sent.
        background_tasks.add_task(
            process_document,
            document_id,
            file_path,
            file_type
        )

        return {
            "id": document_id,
            "filename": stored_filename,
            "original_filename": file.filename,
            "file_type": file_type,
            "status": "pending"
        }

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )
