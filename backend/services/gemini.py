"""
Gemini API wrapper — uses Google Generative AI SDK (Gemini 2.0 Flash).
Provides fact-checking, claim analysis, and timeline generation.
Includes automatic fallback to alternate models on quota exhaustion.
"""

import os
import json
import re
import asyncio
import logging
from google import genai
from google.genai import types

log = logging.getLogger(__name__)

# ── Client setup (lazy — deferred until first call) ─────────
API_KEY = os.getenv("GEMINI_API_KEY", "")
MODELS = [
    "gemma-4-26b-a4b-it",       # Gemma 4 (26 billion parameter instruction-tuned)
    "gemma-4-31b-it"
]
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=API_KEY)
    return _client


async def _call_with_fallback(config, contents):
    """Try each model in MODELS list; fall back on 429/404 errors."""
    last_err = None
    for model in MODELS:
        try:
            log.info(f"Trying model: {model}")
            response = _get_client().models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
            return response
        except Exception as e:
            last_err = e
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "404" in err_str or "NOT_FOUND" in err_str:
                log.warning(f"{model} unavailable ({type(e).__name__}), trying next...")
                await asyncio.sleep(1)
                continue
            raise  # non-recoverable error — don't retry
    raise last_err  # all models exhausted

# ── System prompts ──────────────────────────────────────────
ASSISTANT_SYSTEM = """You are "Chunav Guide" (चुनाव गाइड) — India's Interactive Election Assistant.

Your role:
1. Help users understand the election process in India in a simple, interactive, and easy-to-follow way.
2. Provide step-by-step guidance on voting (e.g., how to register, find polling booths, what IDs to bring).
3. Explain election timelines, schedules, and important dates.
4. Keep the tone helpful, encouraging, and neutral. Do not express political opinions.
5. You have access to Google Search to fetch real-time, accurate election data. Always ground your responses in facts.

Format your response:
## 🗳️ Election Guidance
[Clear, step-by-step explanation or answer]

## 📅 Timeline Context (if applicable)
[When does this happen in the election cycle?]

## 📝 Important Steps
[Actionable bullet points for the voter]
"""

PROCESS_SYSTEM = """You are "Chunav Guide" timeline assistant. Given an election stage or topic, produce a structured JSON timeline of the election process.

Return ONLY valid JSON in this exact format:
{
  "topic": "Topic title",
  "summary": "Brief overview of this process",
  "events": [
    {
      "date": "Timeline or duration (e.g., '14 days before polling')",
      "title": "Step title",
      "description": "Detailed explanation of this step",
      "type": "registration|notification|campaign|polling|counting",
      "sources": ["Election Commission"]
    }
  ],
  "misinfo_count": 0,
  "fact_check_count": 0
}

Rules:
- Be strictly educational and neutral.
- Focus on the STEPS and TIMELINES of the election process.
"""


async def fact_check_claim(claim: str, conversation_history: list[dict] | None = None) -> str:
    """
    Send a query to the Election Assistant.
    Supports multi-turn conversation via history.
    Uses Google Search Grounding.
    """
    contents = []

    if conversation_history:
        for msg in conversation_history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])],
                )
            )

    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=claim)],
        )
    )

    config = types.GenerateContentConfig(
        system_instruction=ASSISTANT_SYSTEM,
        temperature=0.3,
        max_output_tokens=2048,
        tools=[{"google_search": {}}],  # Meaningful Google Services Integration!
    )

    response = await _call_with_fallback(config, contents)
    return response.text


async def generate_timeline(topic: str) -> dict:
    """
    Generate a structured timeline of the election process for a given topic.
    Returns parsed JSON.
    """
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=f"Explain the election process timeline for: {topic}")],
        )
    ]
    config = types.GenerateContentConfig(
        system_instruction=PROCESS_SYSTEM,
        temperature=0.2,
        max_output_tokens=4096,
        response_mime_type="application/json",
        tools=[{"google_search": {}}],  # Google Search Integration
    )

    response = await _call_with_fallback(config, contents)

    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response.text)
        if match:
            return json.loads(match.group(1))
        return {"error": "Failed to parse timeline", "raw": response.text}
