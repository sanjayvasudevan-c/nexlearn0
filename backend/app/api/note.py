import os
import shutil
import uuid

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.note import Note
from app.models.user import User
from app.dependencies.auth import get_current_user


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
        title=title,
        subject=subject,
        content_type=content_type,
        is_private=is_private,
        file_type=file.content_type,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        user_id=current_user.id
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
    note_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    note = db.query(Note).filter(
        Note.id == note_id
    ).first()

    if not note:
        raise HTTPException(status_code=404)

    if note.is_private and note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    note.view_count += 1
    db.commit()

    return FileResponse(
        path=note.file_path,
        media_type=note.file_type
    )


@router.get("/{note_id}/download")
def download_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    note = db.query(Note).filter(
        Note.id == note_id
    ).first()

    if not note:
        raise HTTPException(status_code=404)

    if note.is_private and note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    note.download_count += 1
    db.commit()

    return FileResponse(
        path=note.file_path,
        media_type=note.file_type,
        filename=os.path.basename(note.file_path),
        headers={"Content-Disposition": "attachment"}
    )


@router.post("/{note_id}/upvote")
def upvote_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    note = db.query(Note).filter(
        Note.id == note_id
    ).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if note.is_private and note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    note.upvotes += 1
    db.commit()

    return {
        "message": "Upvoted successfully",
        "total_upvotes": note.upvotes
    }


    