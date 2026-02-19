import app
print("APP MODULE PATH:", app.__file__)

import app.db.session
print("SESSION MODULE PATH:", app.db.session.__file__)

import app.db.session
print("SESSION MODULE PATH:", app.db.session.__file__)

from fastapi import FastAPI
from sqlalchemy import text

from app.db.session import engine
from app.db.base import Base
from app.models.user import User
from app.api.auth import router as auth_router

app = FastAPI(title="Notes API")


@app.on_event("startup")
def check_db():
    # Verify DB connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    # Create tables
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth_router)
