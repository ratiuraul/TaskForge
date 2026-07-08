from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.auth.api.routes import router as auth_router

app = FastAPI(title="TaskForge", version="0.1.0")


@app.get("/")
async def root():
    return {"message": "TaskForge API"}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "detail": str(e)}


app.include_router(auth_router)
