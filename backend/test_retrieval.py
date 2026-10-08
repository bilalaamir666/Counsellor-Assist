from app.services.retrieval_service import search_similar_chunks


results = search_similar_chunks(
    "What is the salary of the developer at MGD TECH?"
)


print(f"\nResults found: {len(results)}\n")


for i, result in enumerate(results, start=1):
    print(f"--- Result {i} ---")
    print(f"Page: {result['page_number']}")
    print(f"Score: {result['score']}")
    print(f"Content:\n{result['content'][:500]}")
    print()
