import json
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.auth import create_access_token
from app.config import settings
from app.guardrails import sanitize_output, validate_query
from app.llm import generate_answer
from app.models import ChatRequest, ChatResponse, IngestRequest, LoginRequest, TokenResponse
from app.monitoring import GUARDRAIL_BLOCKS, LLM_REQUESTS, REQUESTS_TOTAL, track_latency
from app.rbac import User, authenticate_user, require_roles
from app.retriever import Retriever
from app.store import AuditStore


app = FastAPI(title=settings.app_name, version="1.0.0")
retriever = Retriever()
audit_store = AuditStore()


def _seed_data() -> None:
    seed_path = Path(__file__).resolve().parent.parent / "data" / "seed_docs.json"
    if not seed_path.exists():
        return
    docs = json.loads(seed_path.read_text(encoding="utf-8"))
    for doc in docs:
        retriever.ingest(title=doc["title"], source=doc["source"], content=doc["content"])


@app.on_event("startup")
def startup_event() -> None:
    _seed_data()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


@app.post("/auth/token", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    with track_latency("/auth/token"):
        user = authenticate_user(payload.username, payload.password)
        if not user:
            REQUESTS_TOTAL.labels(endpoint="/auth/token", status="unauthorized").inc()
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token(user.username, user.role)
        REQUESTS_TOTAL.labels(endpoint="/auth/token", status="ok").inc()
        audit_store.log("auth.login", user.username, {"role": user.role})
        return TokenResponse(access_token=token, role=user.role)


@app.post("/ingest")
def ingest(
    payload: IngestRequest,
    user: User = Depends(require_roles("admin", "editor")),
) -> dict:
    with track_latency("/ingest"):
        count = retriever.ingest(payload.title, payload.source, payload.content)
        REQUESTS_TOTAL.labels(endpoint="/ingest", status="ok").inc()
        audit_store.log("rag.ingest", user.username, {"title": payload.title, "chunks": count})
        return {"ingested_chunks": count, "title": payload.title}


@app.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    user: User = Depends(require_roles("admin", "editor", "viewer")),
) -> ChatResponse:
    with track_latency("/chat"):
        is_valid, reason = validate_query(payload.query)
        if not is_valid:
            GUARDRAIL_BLOCKS.labels(reason="input_policy").inc()
            REQUESTS_TOTAL.labels(endpoint="/chat", status="blocked").inc()
            audit_store.log(
                "guardrail.blocked",
                user.username,
                {"query": payload.query, "reason": reason},
            )
            return ChatResponse(answer=reason, citations=[], blocked_by_guardrail=True)

        citations = retriever.retrieve(payload.query, top_k=settings.top_k)
        try:
            answer = generate_answer(payload.query, citations)
            LLM_REQUESTS.labels(status="ok").inc()
        except Exception:
            LLM_REQUESTS.labels(status="error").inc()
            joined = " ".join(c["chunk"] for c in citations)
            answer = f"Grounded response for '{payload.query}': {joined[:900]}"
        answer = sanitize_output(answer)

        REQUESTS_TOTAL.labels(endpoint="/chat", status="ok").inc()
        audit_store.log(
            "rag.chat",
            user.username,
            {"query": payload.query, "citations": len(citations)},
        )
        return ChatResponse(answer=answer, citations=citations)


@app.get("/audit")
def audit(user: User = Depends(require_roles("admin"))) -> dict:
    with track_latency("/audit"):
        REQUESTS_TOTAL.labels(endpoint="/audit", status="ok").inc()
        return {"events": audit_store.recent(limit=100)}
