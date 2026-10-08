import sys

sys.path.insert(0, "backend")

from app.database import db


chunks = list(
    db["chunks"].find(
        {},
        {
            "_id": 0,
            "content": 1,
            "page_number": 1
        }
    ).sort("page_number", 1)
)


for chunk in chunks:
    content = chunk["content"].replace("\n", " ")
    print(f'PAGE {chunk["page_number"]}: {content[:500]}')
