import sys
sys.path.insert(0, "backend")

from app.database import db

doc = db["documents"].find_one(
    {"original_filename": "CBIU Student Visa Handbook 2027.pdf"}
)

print(f"DOCUMENT: {doc['original_filename']}")
print(f"ID: {doc['_id']}")

chunks = list(
    db["chunks"].find(
        {"document_id": str(doc["_id"])},
        {"page_number": 1, "content": 1, "chunk_index": 1}
    ).sort("page_number", 1)
)

for chunk in chunks:
    print(f"\n--- PAGE {chunk['page_number']} | CHUNK {chunk['chunk_index']} ---")
    print(chunk["content"])
