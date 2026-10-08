from app.database import db
from app.services.embedding_service import model


chunks_collection = db["chunks"]


def search_similar_chunks(
    query: str,
    limit: int = 5
):
    """
    Convert the user's question into an embedding
    and retrieve the most relevant chunks from MongoDB Atlas.
    """

    query = query.strip()

    if not query:
        raise ValueError("Query cannot be empty")

    query_embedding = model.encode(
        f"query: {query}",
        normalize_embeddings=True
    ).tolist()

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": max(limit * 10, 50),
                "limit": limit
            }
        },
        {
            "$project": {
                "_id": 0,
                "document_id": 1,
                "content": 1,
                "page_number": 1,
                "chunk_index": 1,
                "score": {
                    "$meta": "vectorSearchScore"
                }
            }
        }
    ]

    return list(
        chunks_collection.aggregate(pipeline)
    )
