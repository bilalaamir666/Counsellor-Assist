import sys
sys.path.insert(0, "backend")

from app.database import db

docs = list(
    db["documents"].find(
        {"original_filename": {"$regex": "CBIU|Crescent Bay", "$options": "i"}},
        {"_id": 1, "original_filename": 1}
    )
)

for doc in docs:
    print(f"\n\n{'=' * 80}")
    print(f"DOCUMENT: {doc['original_filename']}")
    print(f"ID: {doc['_id']}")
    print(f"{'=' * 80}")

    chunks = list(
        db["chunks"].find(
            {"document_id": str(doc["_id"])},
            {"page_number": 1, "content": 1, "chunk_index": 1}
        ).sort("page_number", 1)
    )

    for chunk in chunks:
        print(f"\n--- PAGE {chunk['page_number']} | CHUNK {chunk['chunk_index']} ---")
        print(chunk["content"])
