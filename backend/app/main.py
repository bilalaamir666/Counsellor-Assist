from fastapi import FastAPI

from app.database import client, db
from app.routes.auth import router as auth_router


app = FastAPI(
    title="Counsellor Assist API",
    version="1.0.0"
)


app.include_router(auth_router)


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
