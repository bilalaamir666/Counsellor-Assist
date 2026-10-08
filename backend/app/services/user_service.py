from app.database import db
from app.models.user import User, UserRole
from app.utils.security import hash_password


users_collection = db["users"]


def create_user(user: User):
    user_data = user.model_dump()

    result = users_collection.insert_one(user_data)

    return str(result.inserted_id)


def create_user_with_password(
    name: str,
    email: str,
    password: str,
    role: UserRole = "counsellor"
):
    password_hash = hash_password(password)

    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        role=role
    )

    return create_user(user)


def get_user_by_email(email: str):
    return users_collection.find_one({"email": email})
