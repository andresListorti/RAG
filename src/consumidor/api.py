import threading
import time
from collections import deque
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator

from .agent import Agent
from .ingest import ROOT
from .retrieval import Retriever


@asynccontextmanager
async def lifespan(app):
    app.state.agent = Agent(Retriever())
    yield


app = FastAPI(title="Consumidor RAG", version="0.1.0", lifespan=lifespan)
lock = threading.Lock()
recent = deque()
slots = threading.BoundedSemaphore(2)


class Question(BaseModel):
    question: str = Field(min_length=5, max_length=1500)

    @field_validator("question")
    @classmethod
    def clean(cls, value):
        value = value.strip()
        if len(value) < 5 or any(ord(c) < 32 and c not in "\n\t" for c in value):
            raise ValueError("Invalid question")
        return value


@app.middleware("http")
async def protect(request: Request, call_next):
    # Count bytes actually received, rather than trusting Content-Length.
    if request.method == "POST":
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 8192:
                return JSONResponse({"detail": "Request too large"}, status_code=413)
        request._body = bytes(body)
    response = await call_next(request)
    response.headers.update(
        {
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer",
            "Cache-Control": "no-store",
            "X-Frame-Options": "DENY",
        }
    )
    return response


@app.get("/")
def home():
    return FileResponse(ROOT / "web" / "index.html")


@app.get("/app.js")
def javascript():
    return FileResponse(ROOT / "web" / "app.js", media_type="text/javascript")


@app.get("/style.css")
def stylesheet():
    return FileResponse(ROOT / "web" / "style.css", media_type="text/css")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "corpus": app.state.agent.retriever.manifest,
        "retrieval_backend": app.state.agent.retriever.backend,
    }


@app.post("/api/ask")
def ask(body: Question):
    with lock:
        now = time.monotonic()
        while recent and recent[0] < now - 60:
            recent.popleft()
        if len(recent) >= 20:
            raise HTTPException(429, "Límite de la demo: 20 consultas por minuto")
        recent.append(now)
    if not slots.acquire(blocking=False):
        raise HTTPException(429, "La demo está ocupada; reintentá en unos segundos")
    try:
        return app.state.agent.run(body.question)
    except Exception:
        # Do not return exception strings: provider errors can contain request data.
        raise HTTPException(503, "No se pudo completar la consulta") from None
    finally:
        slots.release()
