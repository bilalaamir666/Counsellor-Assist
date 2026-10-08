from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from pydantic import BaseModel, EmailStr, Field

from app.utils.auth import get_current_user

from app.services.enquiry_service import (
    create_enquiry,
    get_all_enquiries,
    get_enquiry_by_id,
    update_enquiry,
)


router = APIRouter(
    prefix="/enquiries",
    tags=["Enquiries"]
)


ENQUIRY_STATUSES = [
    "new",
    "contacted",
    "documents pending",
    "applied",
    "visa in process",
    "closed"
]


# ============================================================
# SCHEMAS
# ============================================================

class EnquiryCreate(BaseModel):
    student_name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    student_email: EmailStr

    student_phone: str = Field(
        ...,
        min_length=5,
        max_length=30
    )

    nationality: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    course: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    intake: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    assigned_counsellor: str | None = None


class EnquiryUpdate(BaseModel):
    status: str | None = None
    assigned_counsellor: str | None = None
    course: str | None = None
    intake: str | None = None


class NoteCreate(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
        max_length=2000
    )


# ============================================================
# CREATE ENQUIRY
# ADMIN + COUNSELLOR
# ============================================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
def create_new_enquiry(
    enquiry_data: EnquiryCreate,
    current_user=Depends(get_current_user)
):

    now = datetime.now(timezone.utc)

    enquiry = {
        **enquiry_data.model_dump(),

        "status": "new",

        "notes": [],

        "status_history": [
            {
                "status": "new",
                "changed_by": str(
                    current_user["_id"]
                ),
                "changed_at": now
            }
        ],

        "created_at": now,
        "updated_at": now
    }

    enquiry_id = create_enquiry(
        enquiry
    )

    return {
        "id": enquiry_id,
        "message": "Enquiry created successfully"
    }


# ============================================================
# LIST ENQUIRIES WITH PAGINATION
# ADMIN + COUNSELLOR
# ============================================================

@router.get("")
def list_enquiries(
    page: int = Query(
        1,
        ge=1,
        description="Page number"
    ),

    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Number of enquiries per page"
    ),

    current_user=Depends(get_current_user)
):

    enquiries = get_all_enquiries()

    total = len(enquiries)

    start = (page - 1) * limit
    end = start + limit

    paginated_enquiries = enquiries[
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
                "id": str(
                    enquiry["_id"]
                ),

                "student_name": enquiry[
                    "student_name"
                ],

                "student_email": enquiry[
                    "student_email"
                ],

                "student_phone": enquiry[
                    "student_phone"
                ],

                "nationality": enquiry[
                    "nationality"
                ],

                "course": enquiry[
                    "course"
                ],

                "intake": enquiry[
                    "intake"
                ],

                "status": enquiry[
                    "status"
                ],

                "assigned_counsellor": enquiry.get(
                    "assigned_counsellor"
                ),

                "notes": enquiry.get(
                    "notes",
                    []
                ),

                "status_history": enquiry.get(
                    "status_history",
                    []
                ),

                "created_at": enquiry[
                    "created_at"
                ],

                "updated_at": enquiry[
                    "updated_at"
                ]
            }

            for enquiry in paginated_enquiries
        ]
    }


# ============================================================
# GET SINGLE ENQUIRY
# ADMIN + COUNSELLOR
# ============================================================

@router.get("/{enquiry_id}")
def get_single_enquiry(
    enquiry_id: str,
    current_user=Depends(get_current_user)
):

    try:
        enquiry = get_enquiry_by_id(
            enquiry_id
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid enquiry ID"
        )

    if not enquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enquiry not found"
        )

    return {
        "id": str(
            enquiry["_id"]
        ),

        "student_name": enquiry[
            "student_name"
        ],

        "student_email": enquiry[
            "student_email"
        ],

        "student_phone": enquiry[
            "student_phone"
        ],

        "nationality": enquiry[
            "nationality"
        ],

        "course": enquiry[
            "course"
        ],

        "intake": enquiry[
            "intake"
        ],

        "status": enquiry[
            "status"
        ],

        "assigned_counsellor": enquiry.get(
            "assigned_counsellor"
        ),

        "notes": enquiry.get(
            "notes",
            []
        ),

        "status_history": enquiry.get(
            "status_history",
            []
        ),

        "created_at": enquiry[
            "created_at"
        ],

        "updated_at": enquiry[
            "updated_at"
        ]
    }


# ============================================================
# UPDATE ENQUIRY
# ADMIN + COUNSELLOR
# ============================================================

@router.patch("/{enquiry_id}")
def update_existing_enquiry(
    enquiry_id: str,
    update_data: EnquiryUpdate,
    current_user=Depends(get_current_user)
):

    try:
        enquiry = get_enquiry_by_id(
            enquiry_id
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid enquiry ID"
        )

    if not enquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enquiry not found"
        )

    changes = {
        key: value
        for key, value in update_data.model_dump().items()
        if value is not None
    }

    # Nothing to update
    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update"
        )

    # Validate status
    if "status" in changes:

        if changes["status"] not in ENQUIRY_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Invalid enquiry status. "
                    "Allowed statuses: "
                    + ", ".join(ENQUIRY_STATUSES)
                )
            )

        # Add status history only when status changes
        if changes["status"] != enquiry["status"]:

            status_history = enquiry.get(
                "status_history",
                []
            )

            status_history.append(
                {
                    "status": changes["status"],

                    "changed_by": str(
                        current_user["_id"]
                    ),

                    "changed_at": datetime.now(
                        timezone.utc
                    )
                }
            )

            changes["status_history"] = (
                status_history
            )

    changes["updated_at"] = datetime.now(
        timezone.utc
    )

    update_enquiry(
        enquiry_id,
        changes
    )

    return {
        "message": "Enquiry updated successfully"
    }


# ============================================================
# ADD NOTE
# ADMIN + COUNSELLOR
# ============================================================

@router.post("/{enquiry_id}/notes")
def add_enquiry_note(
    enquiry_id: str,
    note_data: NoteCreate,
    current_user=Depends(get_current_user)
):

    try:
        enquiry = get_enquiry_by_id(
            enquiry_id
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid enquiry ID"
        )

    if not enquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enquiry not found"
        )

    note = {
        "author_id": str(
            current_user["_id"]
        ),

        "content": note_data.content,

        "created_at": datetime.now(
            timezone.utc
        )
    }

    notes = enquiry.get(
        "notes",
        []
    )

    notes.append(note)

    update_enquiry(
        enquiry_id,
        {
            "notes": notes,

            "updated_at": datetime.now(
                timezone.utc
            )
        }
    )

    return {
        "message": "Note added successfully"
    }