from fastapi import FastAPI

app = FastAPI(
    title="Counsellor Assist API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Counsellor Assist API is running"
    }