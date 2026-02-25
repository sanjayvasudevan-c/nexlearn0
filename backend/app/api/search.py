from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import math

from app.db.session import get_db
from app.ml.embedding_model import generate_embedding

router = APIRouter(prefix="/search", tags=["Search"])

SIMILARITY_THRESHOLD = 0.3
SIMILARITY_WEIGHT = 0.7
ENGAGEMENT_WEIGHT = 0.3


@router.get("/")
def semantic_search(q: str, db: Session = Depends(get_db)):

    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # 1️⃣ Convert query into embedding vector
    query_embedding = generate_embedding(q)

    # 2️⃣ Retrieve semantically closest notes (top 20)
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

    if not rows:
        return {"message": "No notes found"}

    final_results = []

    for row in rows:
        similarity = float(row.similarity)
        engagement = float(row.engagement)

        # 3️⃣ Apply similarity threshold
        if similarity < SIMILARITY_THRESHOLD:
            continue

        # 4️⃣ Compute hybrid final score
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

    if not final_results:
        return {"message": "No relevant notes found"}

    # 5️⃣ Sort by final_score descending
    final_results.sort(key=lambda x: x["final_score"], reverse=True)

    return final_results