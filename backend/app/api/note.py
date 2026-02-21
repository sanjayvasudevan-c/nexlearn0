import os
import shutil
import uuid

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.note import Note
from fastapi.response import FileResponse


router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post("/upload")
def upload_note(
    title: str = Form(...),
    subject: str = Form(...),
    content_type: str = Form(...),
    is_private: bool = Form(True),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if not file.filename:
        raise HTTPException(status_code=400, detail="File missing")

    UPLOAD_DIR = "uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    note = Note(
        title: str = Form(...),
        subject: str = Form(...),
        content_type: str = Form(...),
        is_private: bool = Form(True),
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return {
        "message": "Uploaded successfully",
        "note_id": str(note.id)
    }

@router.get("/{note_id}/view")
def view_note(
    notes_id = str
    db: session = Depends(get_db)
    current_user: User = Depends(get_current_user)
):

    note = db.query(Note).filter(
        Note.id = notes_id,
        Note.user_id = current_user.id  
    )
