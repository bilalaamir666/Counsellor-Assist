from app.database import db


def create_indexes():
    db["users"].create_index(
        "email",
        unique=True
    )

    db["documents"].create_index(
        "status"
    )

    db["documents"].create_index(
        "uploaded_by"
    )

    db["conversations"].create_index(
        [("user_id", 1), ("updated_at", -1)]
    )

    db["enquiries"].create_index(
        "status"
    )

    db["enquiries"].create_index(
        "assigned_counsellor"
    )

    db["enquiries"].create_index(
        [("created_at", -1)]
    )

    print("MongoDB indexes created successfully")


if __name__ == "__main__":
    create_indexes()
