from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from datetime import date

from app.db.session import get_db
from app.ml.embedding_model import generate_embedding
from app.models.demand_log import DemandLog
from app.models.challenge import Challenge
from app.dependencies.auth import get_current_user
from app.utils.topic_normalizer import normalize_topic
from app.services.ai_notes import generate_ai_notes


router = APIRouter(prefix="/search", tags=["Search"])

SIMILARITY_THRESHOLD = 0.40
CANDIDATE_LIMIT = 100

BASE_REWARD = 50
DEMAND_WEIGHT = 5
DAY_WEIGHT = 10


@router.get("/")
def semantic_search(
    q: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Validate query
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    query = q.strip()

    # Generate embedding
    query_embedding = generate_embedding(query)

    # Retrieve candidate notes
    result = db.execute(
        text("""
            SELECT
                id,
                title,
                subject,
                description,
                user_id,
                created_at,
                upvotes,
                view_count,
                download_count,
                embedding <=> :embedding AS distance,
                1 - (embedding <=> :embedding) AS similarity
            FROM notes
            WHERE is_private = false
            ORDER BY embedding <=> :embedding
            LIMIT :limit
        """),
        {
            "embedding": query_embedding,
            "limit": CANDIDATE_LIMIT
        }
    )

    rows = result.fetchall()

    candidates = []

    for row in rows:

        similarity = float(row.similarity)

        if similarity < SIMILARITY_THRESHOLD:
            continue

        candidates.append({
            "id": str(row.id),
            "title": row.title,
            "subject": row.subject,
            "description": row.description,
            "author_id": str(row.user_id),
            "created_at": row.created_at,
            "similarity": similarity,
            "distance": float(row.distance),
            "upvotes": row.upvotes,
            "views": row.view_count,
            "downloads": row.download_count
        })

    # If results exist return them
    if candidates:
        return {
            "query": query,
            "candidate_count": len(candidates),
            "results": candidates,
            "ai_generated_note": None,
            "challenge_available": False
        }

    # Normalize topic
    topic_key = normalize_topic(query)

    # Insert demand log
    try:
        demand = DemandLog(
            query=query,
            topic_key=topic_key,
            user_id=current_user.id,
            search_date=date.today()
        )

        db.add(demand)
        db.commit()

    except IntegrityError:
        db.rollback()

    # Recalculate demand stats
    stats = db.execute(
        text("""
            SELECT
                COUNT(*) AS demand_count,
                COUNT(DISTINCT search_date) AS days_active
            FROM demand_logs
            WHERE topic_key = :topic_key
        """),
        {"topic_key": topic_key}
    ).fetchone()

    demand_count = stats.demand_count
    days_active = stats.days_active

    # Calculate reward
    reward = BASE_REWARD + (demand_count * DEMAND_WEIGHT) + (days_active * DAY_WEIGHT)

    # Check existing challenge
    challenge = db.query(Challenge).filter(
        Challenge.topic_key == topic_key,
        Challenge.is_active == True
    ).first()

    if challenge:
        challenge.reward_credits = reward
        challenge.demand_count = demand_count
        challenge.days_active = days_active
        db.commit()

    else:
        challenge = Challenge(
            topic_key=topic_key,
            reward_credits=reward,
            demand_count=demand_count,
            days_active=days_active,
            is_active=True
        )

        try:
            db.add(challenge)
            db.commit()
            db.refresh(challenge)

        except IntegrityError:
            db.rollback()

            challenge = db.query(Challenge).filter(
                Challenge.topic_key == topic_key
            ).first()

    # Generate AI fallback note
    try:
        ai_note = generate_ai_notes(query)
    except Exception:
        ai_note = None

    return {
        "query": query,
        "results": [],
        "ai_generated_note": ai_note,
        "challenge_available": True,
        "challenge": {
            "challenge_id": str(challenge.id),
            "topic_key": challenge.topic_key,
            "reward_credits": challenge.reward_credits,
            "demand_count": challenge.demand_count,
            "days_active": challenge.days_active
        }
    }