from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.utils.auth import get_current_user
from app.services.retrieval_service import search_similar_chunks
from app.services.llm_service import generate_answer
from app.services.conversation_service import (
    create_conversation,
    add_message,
    get_conversation_by_id,
)
from app.services.document_service import get_document_by_id


router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    conversation_id: str | None = None


class ChatSource(BaseModel):
    document_id: str
    document_name: str
    page_number: int
    snippet: str


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    sources: list[ChatSource]


@router.post("/ask", response_model=ChatResponse)
def ask_question(
    request: ChatRequest,
    current_user=Depends(get_current_user)
):
    conversation_id = request.conversation_id

    # Create a new conversation for the first question
    if conversation_id is None:
        now = datetime.now(timezone.utc)

        conversation_id = create_conversation({
            "user_id": str(current_user["_id"]),
            "messages": [],
            "created_at": now,
            "updated_at": now
        })

        conversation_history = []

    else:
        # Load existing conversation
        conversation = get_conversation_by_id(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Make sure the conversation belongs to the logged-in user
        if conversation["user_id"] != str(current_user["_id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this conversation"
            )

        conversation_history = conversation.get("messages", [])

    # Save the user's message
    user_message = {
        "role": "user",
        "content": request.question,
        "sources": [],
        "created_at": datetime.now(timezone.utc)
    }

    add_message(conversation_id, user_message)

    # Retrieve relevant document chunks
    results = search_similar_chunks(request.question, limit=5)

    if not results:
        answer = "I could not find this information in the provided documents."

        add_message(
            conversation_id,
            {
                "role": "assistant",
                "content": answer,
                "sources": [],
                "created_at": datetime.now(timezone.utc)
            }
        )

        return ChatResponse(
            conversation_id=conversation_id,
            answer=answer,
            sources=[]
        )

    # Generate answer using document chunks + previous conversation
    llm_result = generate_answer(
        request.question,
        results,
        conversation_history
    )

    answer = llm_result["answer"]
    supporting_chunks = llm_result["supporting_chunks"]

    sources = []

    for index in supporting_chunks:
        if isinstance(index, int) and 0 <= index < len(results):
            result = results[index]

            document = get_document_by_id(result["document_id"])

            document_name = result["document_id"]

            if document:
                document_name = document.get(
                    "original_filename",
                    document.get("filename", result["document_id"])
                )

            sources.append(
                ChatSource(
                    document_id=result["document_id"],
                    document_name=document_name,
                    page_number=result["page_number"],
                    snippet=result["content"][:500]
                )
            )

    # Save assistant message
    add_message(
        conversation_id,
        {
            "role": "assistant",
            "content": answer,
            "sources": [
                source.model_dump()
                for source in sources
            ],
            "created_at": datetime.now(timezone.utc)
        }
    )

    return ChatResponse(
        conversation_id=conversation_id,
        answer=answer,
        sources=sources
    )
