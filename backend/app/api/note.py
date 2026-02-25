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
from app.ml.embedding_model import generate_embedding
from app.utils.pdf_utils import extract_text_from_pdf


router = APIRouter(prefix="/notes", tags=["Notes"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)



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

    if not file.content_type or "pdf" not in file.content_type:
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    
    try:
        note_text = extract_text_from_pdf(file_path)
    except Exception:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Failed to extract PDF text")

    if not note_text.strip():
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="PDF contains no readable text")

   
    note_text = note_text[:5000]

   
    embedding = generate_embedding(note_text)

  
    note = Note(
        title=title,
        subject=subject,
        content_type=content_type,
        is_private=is_private,
        file_type=file.content_type,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        user_id=current_user.id,
        embedding=embedding,
        view_count=0,
        download_count=0,
        upvotes=0
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

    note = db.query(Note).filter(Note.id == note_id).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

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

    note = db.query(Note).filter(Note.id == note_id).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

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

    note = db.query(Note).filter(Note.id == note_id).first()

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