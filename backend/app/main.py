from fastapi import FastAPI
from app.database import client, db

app = FastAPI(
    title="Counsellor Assist API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Counsellor Assist API is running"
    }


@app.get("/db-test")
def database_test():
    try:
        client.admin.command("ping")

        return {
            "status": "success",
            "message": "MongoDB connection is working",
            "database": db.name
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }