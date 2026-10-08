import os
import json

from dotenv import load_dotenv
from google import genai

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.8-flash")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured")

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_answer(
    question: str,
    context_chunks: list[dict],
    conversation_history: list[dict] | None = None
) -> dict:

    conversation_history = conversation_history or []

    # Format previous conversation messages
    formatted_history = []

    for message in conversation_history:
        role = message.get("role", "")
        content = message.get("content", "")

        if role in ["user", "assistant"] and content:
            formatted_history.append(
                f"{role.upper()}: {content}"
            )

    history = "\n".join(formatted_history)

    if not history:
        history = "No previous conversation."

    # Format retrieved document chunks
    formatted_chunks = []

    for index, chunk in enumerate(context_chunks):
        formatted_chunks.append(
            f"""
CHUNK {index}

Document ID: {chunk["document_id"]}
Page: {chunk["page_number"]}

Content:
{chunk["content"]}
"""
        )

    context = "\n".join(formatted_chunks)

    prompt = f"""
You are Counsellor Assist, an AI assistant for university counsellors.

Your job is to answer the user's question using ONLY information contained
in the provided reference document chunks.

Previous conversation is provided only to understand what the user means
when asking a follow-up question.

STRICT RULES:

1. Use ONLY the reference document chunks for factual information.
2. Do not use outside knowledge.
3. Do not invent or assume information.
4. Use previous conversation only to understand the context of the user's
   current question.
5. If the reference chunks do not contain enough information to answer
   the current question, refuse to answer.
6. When refusing, use exactly:
   "I could not find this information in the provided documents."
7. Identify which document chunks actually support your answer.
8. Do NOT select a chunk merely because it is related to the topic.
9. If you refuse to answer, supporting_chunks must be an empty list.
10. Return ONLY valid JSON.
11. Do not use Markdown code fences.

Return exactly this structure:

{{
  "answer": "your answer here",
  "supporting_chunks": [0, 2]
}}

The numbers in supporting_chunks must correspond to the CHUNK numbers.

PREVIOUS CONVERSATION:
{history}

REFERENCE DOCUMENT CHUNKS:
{context}

CURRENT USER QUESTION:
{question}
"""

    response = client.interactions.create(
        model=LLM_MODEL,
        input=prompt
    )

    text = response.output_text.strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("Gemini returned invalid JSON")

    if "answer" not in result or "supporting_chunks" not in result:
        raise ValueError("Gemini response is missing required fields")

    if not isinstance(result["supporting_chunks"], list):
        raise ValueError("supporting_chunks must be a list")

    return result
