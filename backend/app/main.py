from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import client, db
from app.routes.auth import router as auth_router
from app.routes.documents import router as documents_router
from app.routes.chat import router as chat_router
from app.routes.conversations import router as conversations_router
from app.routes.enquiries import router as enquiries_router
from app.routes.stats import router as stats_router

app = FastAPI(
    title="Counsellor Assist API",
    version="1.0.0"
)

# Allow the React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(enquiries_router)
app.include_router(stats_router)


@app.get("/")
def root():
    return {"message": "Counsellor Assist API is running"}


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