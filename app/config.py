import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "RAG RBAC Guardrails Monitoring API"
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me-in-production")
    jwt_algorithm: str = "HS256"
    token_exp_minutes: int = 60
    top_k: int = 3
    max_query_chars: int = 500
    chroma_path: str = os.getenv("CHROMA_PATH", "./chroma_data")
    chroma_collection: str = os.getenv("CHROMA_COLLECTION", "knowledge_base")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


settings = Settings()
