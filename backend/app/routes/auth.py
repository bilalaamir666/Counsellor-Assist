from fastapi import APIRouter, HTTPException, status

from app.schemas.user import UserLogin, TokenResponse
from app.services.user_service import get_user_by_email
from app.utils.security import verify_password, create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(user_data: UserLogin):
    user = get_user_by_email(user_data.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(
        user_data.password,
        user["password_hash"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        str(user["_id"]),
        user["role"]
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"]
    }