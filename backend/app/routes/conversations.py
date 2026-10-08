from fastapi import APIRouter, Depends, HTTPException, status

from app.utils.auth import get_current_user
from app.services.conversation_service import (
    get_conversations_by_user,
    get_conversation_by_id,
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"]
)


@router.get("")
def list_conversations(
    current_user=Depends(get_current_user)
):
    conversations = get_conversations_by_user(
        str(current_user["_id"])
    )

    return [
        {
            "id": str(conversation["_id"]),
            "user_id": conversation["user_id"],
            "messages": conversation.get("messages", []),
            "created_at": conversation["created_at"],
            "updated_at": conversation["updated_at"],
        }
        for conversation in conversations
    ]


@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: str,
    current_user=Depends(get_current_user)
):
    try:
        conversation = get_conversation_by_id(conversation_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID"
        )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    if conversation["user_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this conversation"
        )

    return {
        "id": str(conversation["_id"]),
        "user_id": conversation["user_id"],
        "messages": conversation.get("messages", []),
        "created_at": conversation["created_at"],
        "updated_at": conversation["updated_at"],
    }
