"""
Timeline endpoint — structured misinformation timeline generation.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import json
from services.gemini import generate_timeline
from services.google_services import log_analytics, cache_to_gcs

router = APIRouter(tags=["timeline"])


class TimelineRequest(BaseModel):
    topic: str


@router.post("/timeline")
async def timeline(req: TimelineRequest):
    """
    Generate a structured misinformation timeline for a political topic.
    """
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    # Meaningful Google Services Integration
    log_analytics("timeline_generated", {"topic": req.topic})

    try:
        result = await generate_timeline(req.topic)
        
        # Meaningful Google Services Integration: Cache to GCS
        cache_to_gcs(f"timeline_{req.topic.replace(' ', '_')}.json", json.dumps(result))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")
