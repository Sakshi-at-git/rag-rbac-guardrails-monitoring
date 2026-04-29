from time import perf_counter
from contextlib import contextmanager

from prometheus_client import Counter, Histogram


REQUESTS_TOTAL = Counter(
    "rag_requests_total",
    "Total request count by endpoint and status",
    ["endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "rag_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"],
)

GUARDRAIL_BLOCKS = Counter(
    "rag_guardrail_blocks_total",
    "Count of blocked requests by reason",
    ["reason"],
)

LLM_REQUESTS = Counter(
    "rag_llm_requests_total",
    "LLM call count by status",
    ["status"],
)


@contextmanager
def track_latency(endpoint: str):
    start = perf_counter()
    try:
        yield
    finally:
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(perf_counter() - start)
