"""
Timeline endpoint — structured misinformation timeline generation.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.gemini import generate_timeline

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

    try:
        result = await generate_timeline(req.topic)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")
