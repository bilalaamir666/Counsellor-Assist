from fastapi import APIRouter, Depends

from app.utils.auth import get_current_user
from app.services.stats_service import get_enquiry_stats


router = APIRouter(
    prefix="/stats",
    tags=["Statistics"]
)


@router.get("/enquiries")
def enquiry_stats(
    current_user=Depends(get_current_user)
):
    return get_enquiry_stats()
