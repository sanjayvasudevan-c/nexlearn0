from fastapi import FastAPI
from sqlalchemy import text
from app.db.session import engine
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title = "Notes API")

@app.on_event("startup")
def check_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

@app.get("/health")
def health_check():
	return {"status": "ok"}
