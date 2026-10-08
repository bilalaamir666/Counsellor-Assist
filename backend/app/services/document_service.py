from app.database import db


documents_collection = db["documents"]


def create_document(document_data: dict):
    result = documents_collection.insert_one(document_data)

    return str(result.inserted_id)


def get_all_documents():
    return list(
        documents_collection.find().sort("created_at", -1)
    )


def get_document_by_id(document_id):
    from bson import ObjectId

    return documents_collection.find_one(
        {"_id": ObjectId(document_id)}
    )


def delete_document(document_id):
    from bson import ObjectId

    result = documents_collection.delete_one(
        {"_id": ObjectId(document_id)}
    )

    return result.deleted_count
