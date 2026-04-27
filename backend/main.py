"""
Jhooth Pakdo — India's Election Misinformation Firewall
FastAPI backend server
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from routes.chat import router as chat_router
from routes.timeline import router as timeline_router

app = FastAPI(
    title="Jhooth Pakdo API",
    description="AI-powered misinformation detection for Indian elections",
    version="1.0.0",
)

# CORS — allow frontend dev server and deployed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API routes ──────────────────────────────────────────────
app.include_router(chat_router, prefix="/api")
app.include_router(timeline_router, prefix="/api")

# ── Serve frontend static files ────────────────────────────
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/health")
async def health():
    return {"status": "ok", "service": "jhooth-pakdo"}
