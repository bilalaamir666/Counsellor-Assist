import pymongo

from bson import ObjectId

from app.database import db
from app.services.pdf_service import extract_pdf_pages
from app.services.markdown_service import extract_markdown_pages
from app.services.chunking_service import chunk_pages
from app.services.embedding_service import generate_embeddings
from app.services.chunk_service import create_chunks


documents_collection = db["documents"]


def process_document(
    document_id: str,
    file_path: str,
    file_type: str
):
    try:
        object_id = ObjectId(document_id)

        documents_collection.update_one(
            {"_id": object_id},
            {
                "$set": {
                    "status": "processing"
                }
            }
        )

        if file_type == "pdf":
            pages = extract_pdf_pages(file_path)

        elif file_type == "markdown":
            pages = extract_markdown_pages(file_path)

        else:
            raise ValueError("Unsupported document type")

        if not pages:
            raise ValueError(
                "No text could be extracted from document"
            )

        chunks = chunk_pages(
            pages,
            chunk_size=500,
            overlap=100
        )

        if not chunks:
            raise ValueError("No chunks were created")

        texts = [
            chunk["content"]
            for chunk in chunks
        ]

        embeddings = generate_embeddings(texts)

        if len(embeddings) != len(chunks):
            raise ValueError(
                "Number of embeddings does not match number of chunks"
            )

        chunk_documents = []

        for chunk, embedding in zip(chunks, embeddings):
            chunk_documents.append({
                "document_id": document_id,
                "content": chunk["content"],
                "page_number": chunk["page_number"],
                "chunk_index": chunk["chunk_index"],
                "embedding": embedding
            })

        create_chunks(chunk_documents)

        documents_collection.update_one(
            {"_id": object_id},
            {
                "$set": {
                    "status": "ready"
                }
            }
        )

    except Exception as e:
        try:
            documents_collection.update_one(
                {"_id": ObjectId(document_id)},
                {
                    "$set": {
                        "status": "failed",
                        "failure_reason": str(e)
                    }
                }
            )
        except Exception:
            pass

        raise
