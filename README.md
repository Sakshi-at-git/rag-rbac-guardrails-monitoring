<<<<<<< HEAD
# rag-rbac-guardrails-monitoring
This project is a full-stack AI system using RAG to generate accurate responses from external data. It includes RBAC for secure access, guardrails for safe outputs, and monitoring for performance tracking. It demonstrates real-world skills in AI integration, backend development, and system design.
=======
# RAG + RBAC + Guardrails + Monitoring

This project is a complete, local-first Retrieval Augmented Generation (RAG) API built with FastAPI.

It includes:
- **RAG**: persistent ChromaDB retrieval over chunked documents
- **RBAC**: role-based access control with JWT auth (`admin`, `editor`, `viewer`)
- **Guardrails**: input risk detection and output redaction
- **Monitoring**: Prometheus metrics + Grafana dashboards + audit trail
- **LLM**: OpenAI generation with strict grounding prompt and local fallback

## Quick Start (Python)

1. Create virtual env and install:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Run API:

```bash
uvicorn app.main:app --reload
```

3. Open docs:
- Swagger: <http://127.0.0.1:8000/docs>
- Metrics: <http://127.0.0.1:8000/metrics>

## Quick Start (Docker - Full Stack)

```bash
copy .env.example .env
docker compose up --build
```

Then open:
- Swagger: <http://127.0.0.1:8000/docs>
- Metrics: <http://127.0.0.1:8000/metrics>
- Prometheus: <http://127.0.0.1:9090>
- Grafana: <http://127.0.0.1:3000> (`admin` / `admin`)

## Default Users

Use `/auth/token` to obtain JWT.

| Username | Password     | Role   |
|----------|--------------|--------|
| admin    | admin123     | admin  |
| editor   | editor123    | editor |
| viewer   | viewer123    | viewer |

## API Flow

1. `POST /auth/token` -> get bearer token
2. `POST /ingest` (admin/editor) -> add new source documents
3. `POST /chat` (admin/editor/viewer) -> ask questions over indexed docs
4. `GET /metrics` -> monitor system health and usage
5. `GET /audit` (admin only) -> inspect audit events

## Example Curl

```bash
curl -X POST http://127.0.0.1:8000/auth/token ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

Then use returned token:

```bash
curl -X POST http://127.0.0.1:8000/chat ^
  -H "Authorization: Bearer <TOKEN>" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"What does least privilege mean?\"}"
```

## Notes

- Retrieval is persisted to local `chroma_data` volume.
- If `OPENAI_API_KEY` is set, response generation uses OpenAI; otherwise fallback remains local.
- Output answers are grounded in retrieved chunks and sanitized for basic PII.
- Risky requests are blocked with clear guardrail messages.
>>>>>>> 3bd2521 (Initial commit: production-ready RAG stack with RBAC, guardrails, and monitoring.)
