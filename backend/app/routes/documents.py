import os
import shutil
from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
    Query
)

from app.models.document import Document
from app.schemas.document import DocumentUploadResponse

from app.services.document_service import (
    create_document,
    get_all_documents,
    get_document_by_id,
    delete_document
)

from app.services.document_processing_service import (
    process_document
)

from app.utils.auth import require_admin


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


UPLOAD_DIR = "uploads"


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

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

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    if extension not in [".pdf", ".md"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and Markdown files are allowed"
        )

    file_type = (
        "pdf"
        if extension == ".pdf"
        else "markdown"
    )

    os.makedirs(
        UPLOAD_DIR,
        exist_ok=True
    )

    stored_filename = (
        f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        f"{extension}"
    )

    file_path = os.path.join(
        UPLOAD_DIR,
        stored_filename
    )

    try:

        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        now = datetime.now(timezone.utc)

        document = Document(
            filename=stored_filename,
            original_filename=file.filename,
            file_type=file_type,
            status="pending",
            uploaded_by=str(
                current_user["_id"]
            ),
            created_at=now,
            updated_at=now
        )

        document_id = create_document(
            document.model_dump()
        )

        # Process asynchronously after response
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


# ============================================================
# LIST DOCUMENTS WITH PAGINATION
# ============================================================

@router.get("")
def list_documents(
    page: int = Query(
        1,
        ge=1,
        description="Page number"
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Number of documents per page"
    ),
    current_user=Depends(require_admin)
):

    documents = get_all_documents()

    total = len(documents)

    start = (page - 1) * limit
    end = start + limit

    paginated_documents = documents[
        start:end
    ]

    pages = (
        (total + limit - 1) // limit
        if total > 0
        else 0
    )

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
        "items": [
            {
                "id": str(document["_id"]),
                "filename": document["filename"],
                "original_filename": document[
                    "original_filename"
                ],
                "file_type": document["file_type"],
                "status": document["status"],
                "failure_reason": document.get(
                    "failure_reason"
                ),
                "uploaded_by": document[
                    "uploaded_by"
                ],
                "created_at": document[
                    "created_at"
                ],
                "updated_at": document[
                    "updated_at"
                ]
            }
            for document in paginated_documents
        ]
    }


# ============================================================
# GET SINGLE DOCUMENT
# ============================================================

@router.get("/{document_id}")
def get_single_document(
    document_id: str,
    current_user=Depends(require_admin)
):

    try:
        document = get_document_by_id(
            document_id
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID"
        )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return {
        "id": str(
            document["_id"]
        ),
        "filename": document["filename"],
        "original_filename": document[
            "original_filename"
        ],
        "file_type": document["file_type"],
        "status": document["status"],
        "failure_reason": document.get(
            "failure_reason"
        ),
        "uploaded_by": document[
            "uploaded_by"
        ],
        "created_at": document[
            "created_at"
        ],
        "updated_at": document[
            "updated_at"
        ]
    }


# ============================================================
# DELETE DOCUMENT
# ============================================================

@router.delete("/{document_id}")
def remove_document(
    document_id: str,
    current_user=Depends(require_admin)
):

    try:
        document = get_document_by_id(
            document_id
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID"
        )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    deleted_count = delete_document(
        document_id
    )

    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document could not be deleted"
        )

    # Remove physical uploaded file
    file_path = os.path.join(
        UPLOAD_DIR,
        document["filename"]
    )

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass

    return {
        "message": "Document deleted successfully"
    }