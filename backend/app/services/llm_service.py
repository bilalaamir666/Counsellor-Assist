import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not configured")

client = Groq(api_key=GROQ_API_KEY)


def generate_answer(
    question: str,
    context_chunks: list[dict],
    conversation_history: list[dict] | None = None
) -> dict:

    conversation_history = conversation_history or []

    messages = [
        {
            "role": "system",
            "content": """
You are Counsellor Assist, an AI assistant for university counsellors.

Your job is to answer questions using ONLY the provided reference
document chunks.

STRICT RULES:

1. Use ONLY information contained in the reference document chunks.
2. Never use outside knowledge.
3. Never invent or assume information.
4. Previous conversation may only be used to understand follow-up questions.
5. If the provided chunks do not contain enough information to answer
   the current question, refuse to answer.
6. When refusing, use EXACTLY:
   "I could not find this information in the provided documents."
7. Only select chunks that directly support your answer.
8. If refusing, supporting_chunks MUST be an empty list.
9. Return ONLY valid JSON.
10. Do not use Markdown code fences.

Return exactly this structure:

{
  "answer": "your answer here",
  "supporting_chunks": [0, 2]
}

The numbers in supporting_chunks must correspond to the supplied
CHUNK numbers.
"""
        }
    ]

    if conversation_history:
        for message in conversation_history:
            role = message.get("role")
            content = message.get("content")

            if role in ["user", "assistant"] and content:
                messages.append({
                    "role": role,
                    "content": content
                })

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

    user_prompt = f"""
REFERENCE DOCUMENT CHUNKS:

{context}

CURRENT USER QUESTION:

{question}

Remember:
- Answer only from the reference chunks.
- If the answer is not supported by the chunks, use the exact refusal.
- Return valid JSON only.
"""

    messages.append({
        "role": "user",
        "content": user_prompt
    })

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0,
        max_tokens=500
    )

    text = response.choices[0].message.content.strip()

    # Remove accidental Markdown fences if the model adds them.
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        raise ValueError(
            f"Groq returned invalid JSON: {text}"
        )

    if "answer" not in result:
        raise ValueError("Groq response missing 'answer'")

    if "supporting_chunks" not in result:
        raise ValueError(
            "Groq response missing 'supporting_chunks'"
        )

    if not isinstance(result["supporting_chunks"], list):
        raise ValueError(
            "supporting_chunks must be a list"
        )

    return result
