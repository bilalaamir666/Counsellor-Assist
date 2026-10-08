from fastapi import FastAPI

from app.database import client, db
from app.routes.auth import router as auth_router
from app.routes.documents import router as documents_router
from app.routes.chat import router as chat_router
from app.routes.conversations import router as conversations_router


app = FastAPI(
    title="Counsellor Assist API",
    version="1.0.0"
)


app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(conversations_router)


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
