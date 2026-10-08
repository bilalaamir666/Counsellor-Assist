from app.database import db


chunks_collection = db["chunks"]


def create_chunk(chunk_data: dict):
    result = chunks_collection.insert_one(chunk_data)

    return str(result.inserted_id)


def create_chunks(chunk_data_list: list[dict]):
    if not chunk_data_list:
        return []

    result = chunks_collection.insert_many(chunk_data_list)

    return [
        str(chunk_id)
        for chunk_id in result.inserted_ids
    ]


def get_chunks_by_document(document_id: str):
    return list(
        chunks_collection.find(
            {"document_id": document_id}
        ).sort("chunk_index", 1)
    )


def delete_chunks_by_document(document_id: str):
    result = chunks_collection.delete_many(
        {"document_id": document_id}
    )

    return result.deleted_count
