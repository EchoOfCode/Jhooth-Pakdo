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
FACT_CHECK_SYSTEM = """You are "Jhooth Pakdo" (झूठ पकड़ो) — India's election misinformation detection AI.

Your role:
1. Analyse any claim, news headline, WhatsApp forward, or social-media post related to Indian politics/elections.
2. Determine a VERDICT: TRUE ✅, FALSE ❌, MISLEADING ⚠️, UNVERIFIABLE 🔍, or SATIRE 🎭.
3. Provide a clear, sourced explanation in simple language (Hindi-English mix is fine).
4. Suggest what a citizen should do (share, ignore, report).

Rules:
- Be politically NEUTRAL. Never favour any party.
- Cite verifiable sources (Election Commission of India, PIB Fact Check, reputable news).
- If you're unsure, say so — never fabricate certainty.
- Flag common manipulation tactics (deepfakes, out-of-context clips, doctored screenshots).
- Respond in the same language the user writes in (Hindi, English, or Hinglish).
- Keep responses concise but thorough.
- Use bullet points for readability.
- Always end with a "🛡️ Citizen Action" recommendation.

Format your response as follows:
## 🔎 Claim Analysis
[Brief restatement of the claim]

## 📊 Verdict: [VERDICT EMOJI + LABEL]
[Confidence: High/Medium/Low]

## 📝 Explanation
[Detailed analysis with sources]

## 🛡️ Citizen Action
[What should the reader do?]
"""

TIMELINE_SYSTEM = """You are "Jhooth Pakdo" timeline analyst. Given a topic related to Indian elections or politics, produce a structured JSON timeline of key events, misinformation incidents, and fact-checks.

Return ONLY valid JSON in this exact format:
{
  "topic": "Topic title",
  "summary": "Brief overview",
  "events": [
    {
      "date": "YYYY-MM-DD or approximate",
      "title": "Event title",
      "description": "What happened",
      "type": "fact|misinfo|correction|event",
      "sources": ["source1", "source2"]
    }
  ],
  "misinfo_count": 0,
  "fact_check_count": 0
}

Rules:
- Be politically neutral.
- Only include verifiable events.
- Mark misinformation clearly.
- Include corrections/fact-checks where applicable.
- Sort events chronologically.
"""


async def fact_check_claim(claim: str, conversation_history: list[dict] | None = None) -> str:
    """
    Send a claim to Gemini for fact-checking analysis.
    Supports multi-turn conversation via history.
    """
    contents = []

    # Add conversation history if provided
    if conversation_history:
        for msg in conversation_history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])],
                )
            )

    # Add the current claim
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=claim)],
        )
    )

    config = types.GenerateContentConfig(
        system_instruction=FACT_CHECK_SYSTEM,
        temperature=0.3,  # Low temperature for factual accuracy
        max_output_tokens=2048,
    )

    response = await _call_with_fallback(config, contents)
    return response.text


async def generate_timeline(topic: str) -> dict:
    """
    Generate a structured misinformation timeline for a given topic.
    Returns parsed JSON.
    """
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=f"Create a misinformation timeline for: {topic}")],
        )
    ]
    config = types.GenerateContentConfig(
        system_instruction=TIMELINE_SYSTEM,
        temperature=0.2,
        max_output_tokens=4096,
        response_mime_type="application/json",
    )

    response = await _call_with_fallback(config, contents)

    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        # Attempt to extract JSON from markdown code fences
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response.text)
        if match:
            return json.loads(match.group(1))
        return {"error": "Failed to parse timeline", "raw": response.text}
