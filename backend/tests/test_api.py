"""
Tests for Jhooth Pakdo API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

# Adjust path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app

client = TestClient(app)


def test_health_check():
    """Health endpoint should return 200 with service name."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "jhooth-pakdo"


def test_chat_empty_claim():
    """Empty claim should return 400."""
    response = client.post("/api/chat", json={"claim": ""})
    assert response.status_code == 400


def test_chat_missing_claim():
    """Missing claim field should return 422."""
    response = client.post("/api/chat", json={})
    assert response.status_code == 422


def test_timeline_empty_topic():
    """Empty topic should return 400."""
    response = client.post("/api/timeline", json={"topic": ""})
    assert response.status_code == 400


def test_timeline_missing_topic():
    """Missing topic field should return 422."""
    response = client.post("/api/timeline", json={})
    assert response.status_code == 422


@patch("routes.chat.fact_check_claim", new_callable=AsyncMock)
def test_chat_success(mock_gemini):
    """Successful fact-check should return analysis."""
    mock_gemini.return_value = "## Verdict: FALSE ❌\nThis claim is false."
    response = client.post("/api/chat", json={"claim": "India has 50 states"})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "FALSE" in data["analysis"]


@patch("routes.timeline.generate_timeline", new_callable=AsyncMock)
def test_timeline_success(mock_timeline):
    """Successful timeline generation should return structured data."""
    mock_timeline.return_value = {
        "topic": "EVM Controversy",
        "summary": "Test summary",
        "events": [],
        "misinfo_count": 0,
        "fact_check_count": 0,
    }
    response = client.post("/api/timeline", json={"topic": "EVM Controversy"})
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "EVM Controversy"


@patch("routes.chat.fact_check_claim", new_callable=AsyncMock)
def test_chat_with_history(mock_gemini):
    """Chat with conversation history should work."""
    mock_gemini.return_value = "Follow-up analysis."
    response = client.post(
        "/api/chat",
        json={
            "claim": "Tell me more",
            "history": [
                {"role": "user", "content": "Is EVM hackable?"},
                {"role": "assistant", "content": "Let me analyse..."},
            ],
        },
    )
    assert response.status_code == 200
    mock_gemini.assert_called_once()
