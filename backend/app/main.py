from fastapi import FastAPI
from sqlalchemy import text
from app.db.session import engine
from dotenv import load_dotenv
from app.db.base import Base


from app.api.auth import router as auth_router   # ← ADD THIS

load_dotenv()

app = FastAPI(title="Notes API")

@app.on_event("startup")
def check_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Include auth routes
app.include_router(auth_router)   # ← ADD THIS
