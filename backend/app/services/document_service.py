from bson import ObjectId

from app.database import db


documents_collection = db["documents"]
chunks_collection = db["chunks"]


# ============================================================
# CREATE DOCUMENT
# ============================================================

def create_document(document_data: dict):
    result = documents_collection.insert_one(
        document_data
    )

    return str(result.inserted_id)


# ============================================================
# GET ALL DOCUMENTS
# ============================================================

def get_all_documents():
    return list(
        documents_collection
        .find()
        .sort("created_at", -1)
    )


# ============================================================
# GET DOCUMENT BY ID
# ============================================================

def get_document_by_id(document_id: str):

    return documents_collection.find_one(
        {
            "_id": ObjectId(document_id)
        }
    )


# ============================================================
# DELETE DOCUMENT + ITS RAG CHUNKS
# ============================================================

def delete_document(document_id: str):

    object_id = ObjectId(document_id)

    # Delete document
    result = documents_collection.delete_one(
        {
            "_id": object_id
        }
    )

    # If document did not exist
    if result.deleted_count == 0:
        return 0

    # Delete all chunks/embeddings belonging
    # to this document
    chunks_collection.delete_many(
        {
            "document_id": document_id
        }
    )

    return result.deleted_count