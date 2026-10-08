from app.database import db


enquiries_collection = db["enquiries"]


def get_enquiry_stats():
    status_counts = list(
        enquiries_collection.aggregate([
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            }
        ])
    )

    eight_weeks_ago = __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc
    ) - __import__("datetime").timedelta(weeks=8)

    weekly_new = list(
        enquiries_collection.aggregate([
            {
                "$match": {
                    "created_at": {"$gte": eight_weeks_ago}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ])
    )

    top_courses = list(
        enquiries_collection.aggregate([
            {
                "$group": {
                    "_id": "$course",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            },
            {
                "$limit": 5
            }
        ])
    )

    applied_pipeline = [
        {
            "$match": {
                "status_history.status": "applied"
            }
        },
        {
            "$project": {
                "created_at": 1,
                "status_history": 1
            }
        }
    ]

    applied_enquiries = list(
        enquiries_collection.aggregate(applied_pipeline)
    )

    durations = []

    for enquiry in applied_enquiries:
        applied_date = None

        for change in enquiry.get("status_history", []):
            if change.get("status") == "applied":
                applied_date = change.get("changed_at")
                break

        if applied_date:
            created_at = enquiry.get("created_at")

            if created_at:
                duration = (
                    applied_date - created_at
                ).total_seconds() / 86400

                durations.append(duration)

    average_days = (
        round(sum(durations) / len(durations), 2)
        if durations
        else 0
    )

    return {
        "status_counts": [
            {
                "status": item["_id"],
                "count": item["count"]
            }
            for item in status_counts
        ],
        "new_per_week": [
            {
                "week": item["_id"],
                "count": item["count"]
            }
            for item in weekly_new
        ],
        "top_courses": [
            {
                "course": item["_id"],
                "count": item["count"]
            }
            for item in top_courses
        ],
        "average_days_new_to_applied": average_days
    }
