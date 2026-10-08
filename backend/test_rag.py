from app.services.retrieval_service import search_similar_chunks
from app.services.llm_service import generate_answer


question = "What is the expected effort for this assignment?"

results = search_similar_chunks(question, limit=5)

context_parts = []

for result in results:
    context_parts.append(
        f"""
Document ID: {result["document_id"]}
Page: {result["page_number"]}
Content:
{result["content"]}
"""
    )

context = "\n".join(context_parts)

answer = generate_answer(question, context)

print("\nQUESTION:")
print(question)

print("\nANSWER:")
print(answer)

print("\nSOURCES USED:")
for result in results:
    print(
        f"- Page {result['page_number']} "
        f"(score: {result['score']:.4f})"
    )
