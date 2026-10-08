from app.database import db


enquiries_collection = db["enquiries"]


def create_enquiry(enquiry_data: dict):
    result = enquiries_collection.insert_one(enquiry_data)

    return str(result.inserted_id)


def get_all_enquiries():
    return list(
        enquiries_collection.find().sort("created_at", -1)
    )


def get_enquiry_by_id(enquiry_id: str):
    from bson import ObjectId

    return enquiries_collection.find_one(
        {"_id": ObjectId(enquiry_id)}
    )


def update_enquiry(enquiry_id: str, update_data: dict):
    from bson import ObjectId

    result = enquiries_collection.update_one(
        {"_id": ObjectId(enquiry_id)},
        {"$set": update_data}
    )

    return result.modified_count


def delete_enquiry(enquiry_id: str):
    from bson import ObjectId

    result = enquiries_collection.delete_one(
        {"_id": ObjectId(enquiry_id)}
    )

    return result.deleted_count
