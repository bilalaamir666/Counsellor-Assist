import sys
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parent.parent / "backend"
    )
)

from datetime import datetime, timedelta, timezone
import random

from app.database import db


enquiries_collection = db["enquiries"]


# ============================================================
# STUDENTS
# ============================================================

students = [
    ("Ali Khan", "ali.khan@example.com", "03001234567", "Pakistani"),
    ("Sara Ahmed", "sara.ahmed@example.com", "03011234567", "Pakistani"),
    ("Hamza Malik", "hamza.malik@example.com", "03021234567", "Pakistani"),
    ("Ayesha Noor", "ayesha.noor@example.com", "03031234567", "Pakistani"),
    ("Usman Tariq", "usman.tariq@example.com", "03041234567", "Pakistani"),
    ("Hina Shah", "hina.shah@example.com", "03051234567", "Pakistani"),
    ("Bilal Raza", "bilal.raza@example.com", "03061234567", "Pakistani"),
    ("Fatima Zahra", "fatima.zahra@example.com", "03071234567", "Pakistani"),
    ("Omar Farooq", "omar.farooq@example.com", "03081234567", "Pakistani"),
    ("Maham Iqbal", "maham.iqbal@example.com", "03091234567", "Pakistani"),
    ("Zain Abbas", "zain.abbas@example.com", "03101234567", "Pakistani"),
    ("Laiba Hassan", "laiba.hassan@example.com", "03111234567", "Pakistani"),
    ("Danish Ali", "danish.ali@example.com", "03121234567", "Pakistani"),
    ("Iqra Javed", "iqra.javed@example.com", "03131234567", "Pakistani"),
    ("Saad Hussain", "saad.hussain@example.com", "03141234567", "Pakistani"),
    ("Maryam Aslam", "maryam.aslam@example.com", "03151234567", "Pakistani"),
    ("Talha Sheikh", "talha.sheikh@example.com", "03161234567", "Pakistani"),
    ("Sana Waqar", "sana.waqar@example.com", "03171234567", "Pakistani"),
    ("Ahmed Nawaz", "ahmed.nawaz@example.com", "03181234567", "Pakistani"),
    ("Noor Fatima", "noor.fatima@example.com", "03191234567", "Pakistani"),
    ("Kashif Mehmood", "kashif.mehmood@example.com", "03201234567", "Pakistani"),
    ("Anum Saeed", "anum.saeed@example.com", "03211234567", "Pakistani"),
    ("Haris Yousaf", "haris.yousaf@example.com", "03221234567", "Pakistani"),
    ("Eman Tariq", "eman.tariq@example.com", "03231234567", "Pakistani"),
    ("Waleed Akhtar", "waleed.akhtar@example.com", "03241234567", "Pakistani"),
    ("Mina Khan", "mina.khan@example.com", "03251234567", "Pakistani"),
    ("Arham Butt", "arham.butt@example.com", "03261234567", "Pakistani"),
    ("Komal Rauf", "komal.rauf@example.com", "03271234567", "Pakistani"),
    ("Rayan Shah", "rayan.shah@example.com", "03281234567", "Pakistani"),
    ("Alina Malik", "alina.malik@example.com", "03291234567", "Pakistani"),
]


# ============================================================
# REFERENCE VALUES
# ============================================================

courses = [
    "BS Computer Science",
    "BS Artificial Intelligence",
    "BS Software Engineering",
    "BS Data Science",
    "BS Information Technology",
]


intakes = [
    "Spring 2027",
    "Fall 2027",
]


statuses = [
    "new",
    "contacted",
    "documents pending",
    "applied",
    "visa in process",
    "closed",
]


status_order = [
    "new",
    "contacted",
    "documents pending",
    "applied",
    "visa in process",
    "closed",
]


counsellors = [
    "Ahmed Counsellor",
    "Sara Counsellor",
]


# ============================================================
# CREATE SEED DATA
# ============================================================

def create_seed_data():

    # Remove previous seed enquiries
    enquiries_collection.delete_many({
        "student_email": {
            "$regex": "@example\\.com$"
        }
    })

    now = datetime.now(timezone.utc)

    documents = []

    for index, student in enumerate(students):

        name, email, phone, nationality = student

        # ----------------------------------------------------
        # Create date
        # Always between 1 and 59 days ago.
        # ----------------------------------------------------

        age_days = random.randint(1, 59)

        created_at = now - timedelta(
            days=age_days,
            hours=random.randint(0, 20),
            minutes=random.randint(0, 59)
        )

        # ----------------------------------------------------
        # Select deterministic sample values
        # ----------------------------------------------------

        status = statuses[
            index % len(statuses)
        ]

        course = courses[
            index % len(courses)
        ]

        intake = intakes[
            index % len(intakes)
        ]

        counsellor = counsellors[
            index % len(counsellors)
        ]

        # ----------------------------------------------------
        # Build status history
        # ----------------------------------------------------

        target_index = status_order.index(
            status
        )

        status_history = [
            {
                "status": "new",
                "changed_by": "seed-script",
                "changed_at": created_at
            }
        ]

        current_time = created_at

        # Move through status history
        for next_status in status_order[
            1:target_index + 1
        ]:

            current_time += timedelta(
                days=random.randint(1, 3)
            )

            # ------------------------------------------------
            # IMPORTANT:
            # Never allow status changes to be in the future.
            # ------------------------------------------------

            if current_time > now:
                current_time = now

            status_history.append({
                "status": next_status,
                "changed_by": "seed-script",
                "changed_at": current_time
            })

        # ----------------------------------------------------
        # Notes
        # ----------------------------------------------------

        note_time = created_at + timedelta(
            hours=2
        )

        if note_time > now:
            note_time = now

        notes = [
            {
                "author_id": "seed-script",
                "content": (
                    f"Initial enquiry for {course}."
                ),
                "created_at": note_time
            }
        ]

        # ----------------------------------------------------
        # Create enquiry document
        # ----------------------------------------------------

        documents.append({
            "student_name": name,
            "student_email": email,
            "student_phone": phone,
            "nationality": nationality,
            "course": course,
            "intake": intake,
            "status": status,
            "assigned_counsellor": counsellor,
            "notes": notes,
            "status_history": status_history,
            "created_at": created_at,
            "updated_at": current_time,
        })

    # --------------------------------------------------------
    # Insert all enquiries
    # --------------------------------------------------------

    result = enquiries_collection.insert_many(
        documents
    )

    print(
        f"Created {len(result.inserted_ids)} enquiries."
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    create_seed_data()