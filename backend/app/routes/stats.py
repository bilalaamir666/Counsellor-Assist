from fastapi import APIRouter, Depends

from app.utils.auth import require_admin

from app.services.stats_service import get_enquiry_stats


router = APIRouter(
    prefix="/stats",
    tags=["Statistics"]
)


# ============================================================
# ENQUIRY STATISTICS
# ADMIN ONLY
# ============================================================

@router.get("/enquiries")
def enquiry_stats(
    current_user=Depends(require_admin)
):
    return get_enquiry_stats()