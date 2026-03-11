from fastapi import FastAPI
from sqlalchemy import text

from app.db.session import engine
from app.db.base import Base

from app.api.auth import router as auth_router
from app.api.note import router as note_router
from app.api.search import router as search_router
from app.api.challenge import router as challenge_router



app = FastAPI(title="Notes API")


# Register API routers
app.include_router(auth_router)
app.include_router(note_router)
app.include_router(search_router)
app.include_router(challenge_router)


@app.on_event("startup")
def startup_event():

    # Check database connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    # Create tables (development only)
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok"}