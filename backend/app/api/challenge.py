from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.models.challenge import Challenge
from app.models.challenge_submission import ChallengeSubmission
from app.models.note import Note
from app.models.user import User
from app.dependencies.auth import get_current_user


router = APIRouter(prefix="/challenges", tags=["Challenges"])


# -----------------------------
# Get all active challenges
# -----------------------------
@router.get("/")
def list_active_challenges(db: Session = Depends(get_db)):

    challenges = (
        db.query(Challenge)
        .filter(Challenge.is_active == True)
        .order_by(Challenge.reward_credits.desc())
        .all()
    )

    results = []

    for c in challenges:
        results.append({
            "challenge_id": str(c.id),
            "topic_key": c.topic_key,
            "reward_credits": c.reward_credits,
            "demand_count": c.demand_count,
            "days_active": c.days_active
        })

    return {
        "total": len(results),
        "challenges": results
    }


# -----------------------------
# Get single challenge
# -----------------------------
@router.get("/{challenge_id}")
def get_challenge(challenge_id: str, db: Session = Depends(get_db)):

    challenge = db.query(Challenge).filter(
        Challenge.id == challenge_id
    ).first()

    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    return {
        "challenge_id": str(challenge.id),
        "topic_key": challenge.topic_key,
        "reward_credits": challenge.reward_credits,
        "demand_count": challenge.demand_count,
        "days_active": challenge.days_active,
        "is_active": challenge.is_active
    }


# -----------------------------
# Submit note to challenge
# -----------------------------
@router.post("/{challenge_id}/submit")
def submit_note_to_challenge(
    challenge_id: str,
    note_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    challenge = db.query(Challenge).filter(
        Challenge.id == challenge_id,
        Challenge.is_active == True
    ).first()

    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    note = db.query(Note).filter(Note.id == note_id).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if note.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only submit your own notes"
        )

    submission = ChallengeSubmission(
        challenge_id=challenge.id,
        note_id=note.id,
        user_id=current_user.id
    )

    try:
        db.add(submission)
        db.commit()
        db.refresh(submission)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="This note is already submitted to this challenge"
        )

    return {
        "message": "Note submitted to challenge",
        "submission_id": str(submission.id),
        "status": submission.status
    }


# -----------------------------
# Approve submission
# -----------------------------
@router.post("/submissions/{submission_id}/approve")
def approve_submission(
    submission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    submission = db.query(ChallengeSubmission).filter(
        ChallengeSubmission.id == submission_id
    ).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    challenge = db.query(Challenge).filter(
        Challenge.id == submission.challenge_id
    ).first()

    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    user = db.query(User).filter(
        User.id == submission.user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # approve submission
    submission.status = "APPROVED"

    # close challenge
    challenge.is_active = False

    # reward credits
    user.credits += challenge.reward_credits

    db.commit()

    return {
        "message": "Submission approved",
        "reward_given": challenge.reward_credits,
        "user_total_credits": user.credits
    }