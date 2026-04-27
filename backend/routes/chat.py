"""
Chat endpoint — multi-turn fact-checking conversation with Gemini.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.gemini import fact_check_claim
from services.google_services import log_analytics, translate_guidance

router = APIRouter(tags=["chat"])


class MessageIn(BaseModel):
    claim: str
    history: list[dict] | None = None
    target_lang: str | None = None


class MessageOut(BaseModel):
    analysis: str
    ok: bool = True


@router.post("/chat", response_model=MessageOut)
async def chat(msg: MessageIn):
    """
    Analyse a claim / forward / headline.
    Accepts optional conversation history for follow-up questions.
    """
    if not msg.claim.strip():
        raise HTTPException(status_code=400, detail="Claim text cannot be empty.")

    # Meaningful Google Services Integration
    log_analytics("chat_query", {"query_snippet": msg.claim[:50]})

    try:
        result = await fact_check_claim(msg.claim, msg.history)
        
        # Translate if requested
        if msg.target_lang:
            result = translate_guidance(result, msg.target_lang)
            
        return MessageOut(analysis=result)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")
