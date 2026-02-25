from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date

from app.db.session import get_db
from app.ml.embedding_model import generate_embedding
from app.models.demand_log import DemandLog
from app.models.challenge import Challenge
from app.dependencies.auth import get_current_user
from app.utils.topic_normalizer import normalize_topic


router = APIRouter(prefix="/search", tags=["Search"])

SIMILARITY_THRESHOLD = 0.3
SIMILARITY_WEIGHT = 0.7
ENGAGEMENT_WEIGHT = 0.3
BASE_REWARD = 50
REWARD_INCREMENT = 10


@router.get("/")
def semantic_search(
    q: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    # 🔹 1️⃣ Validate Query
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # 🔹 2️⃣ Generate embedding for semantic search
    query_embedding = generate_embedding(q)

    # 🔹 3️⃣ Retrieve candidate notes
    result = db.execute(
        text("""
            SELECT id, title, subject,
                   upvotes, view_count, download_count,
                   1 - (embedding <=> :embedding) AS similarity,
                   (
                       log(1 + view_count)
                       + 2 * upvotes
                       + 0.5 * log(1 + download_count)
                   ) AS engagement
            FROM notes
            WHERE is_private = false
            ORDER BY embedding <=> :embedding
            LIMIT 20
        """),
        {"embedding": query_embedding}
    )

    rows = result.fetchall()

    final_results = []

    # 🔹 4️⃣ Apply hybrid ranking
    for row in rows:
        similarity = float(row.similarity)
        engagement = float(row.engagement)

        if similarity < SIMILARITY_THRESHOLD:
            continue

        final_score = (
            SIMILARITY_WEIGHT * similarity
            + ENGAGEMENT_WEIGHT * engagement
        )

        final_results.append({
            "id": str(row.id),
            "title": row.title,
            "subject": row.subject,
            "similarity": round(similarity, 4),
            "engagement_score": round(engagement, 4),
            "final_score": round(final_score, 4),
            "upvotes": row.upvotes,
            "views": row.view_count,
            "downloads": row.download_count
        })

    # 🔹 5️⃣ If no relevant results → log demand & manage challenge
    if not final_results:

        topic_key = normalize_topic(q)

        # Log demand (unique per user per day)
        try:
            demand = DemandLog(
                query=q.strip(),
                topic_key=topic_key,
                user_id=current_user.id,
                search_date=date.today()
            )
            db.add(demand)
            db.commit()
        except Exception:
            db.rollback()

        # Check if challenge exists
        existing_challenge = db.query(Challenge).filter(
            Challenge.topic_key == topic_key,
            Challenge.is_active == True
        ).first()

        if existing_challenge:
            # Increase reward dynamically
            existing_challenge.reward_credits += REWARD_INCREMENT
            existing_challenge.demand_count += 1
            db.commit()
        else:
            # Create new challenge immediately (threshold = 1)
            new_challenge = Challenge(
                topic_key=topic_key,
                reward_credits=BASE_REWARD,
                demand_count=1,
                is_active=True
            )
            db.add(new_challenge)
            db.commit()

        return {
            "message": "No relevant notes found.",
            "demand_logged": True,
            "topic_key": topic_key
        }

    # 🔹 6️⃣ Sort by final_score descending
    final_results.sort(key=lambda x: x["final_score"], reverse=True)

    return final_results