from app.database import db


conversations_collection = db["conversations"]


def create_conversation(conversation_data: dict):
    result = conversations_collection.insert_one(conversation_data)

    return str(result.inserted_id)


def get_conversations_by_user(user_id: str):
    return list(
        conversations_collection.find(
            {"user_id": user_id}
        ).sort("updated_at", -1)
    )


def get_conversation_by_id(conversation_id: str):
    from bson import ObjectId

    return conversations_collection.find_one(
        {"_id": ObjectId(conversation_id)}
    )


def update_conversation(conversation_id: str, update_data: dict):
    from bson import ObjectId

    result = conversations_collection.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$set": update_data}
    )

    return result.modified_count
