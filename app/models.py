from pydantic import BaseModel, Field
from typing import List


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class IngestRequest(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    content: str = Field(min_length=20, max_length=10000)
    source: str = Field(default="manual")


class ChatRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)


class RetrievedChunk(BaseModel):
    title: str
    source: str
    score: float
    chunk: str


class ChatResponse(BaseModel):
    answer: str
    citations: List[RetrievedChunk]
    blocked_by_guardrail: bool = False
