from fastapi import FastAPI

app = FastAPI(
    title="TaskForge",
    version="0.1.0"
)


@app.get("/")
async def root():
    return {"message": "TaskForge API"}