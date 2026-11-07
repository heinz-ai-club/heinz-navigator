"""
The Heinz Navigator web server.

Routes: the chat page, /api/health, /api/ask, /api/check.
The real work happens in ask/service.py and check/service.py.
"""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.schemas import AskRequest, AskResponse, CheckRequest, CheckResponse
from ask import service as ask_service
from check import service as check_service

logger = logging.getLogger("navigator")

STATIC_DIR = Path(__file__).resolve().parent.parent / "interface" / "static"

app = FastAPI(title="Heinz Navigator")  # CORS is off by default
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

SERVER_ERROR = {"detail": "Something went wrong. Please try again."}


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/ask", response_model=AskResponse)
def ask(req: AskRequest):
    try:
        return ask_service.answer(req.question)
    except Exception:
        # Log the details; never show stack traces or keys to the user.
        logger.exception("ask failed")
        return JSONResponse(SERVER_ERROR, status_code=500)


@app.post("/api/check", response_model=CheckResponse)
def check(req: CheckRequest):
    try:
        return check_service.check(req.program, req.completed_courses, req.notes)
    except Exception:
        logger.exception("check failed")
        return JSONResponse(SERVER_ERROR, status_code=500)
