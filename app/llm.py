from openai import OpenAI

from app.config import settings


def _format_context(citations: list[dict]) -> str:
    blocks = []
    for idx, c in enumerate(citations, start=1):
        blocks.append(
            f"[{idx}] title={c['title']} source={c['source']} score={c['score']:.3f}\n{c['chunk']}"
        )
    return "\n\n".join(blocks)


def generate_answer(query: str, citations: list[dict]) -> str:
    if not citations:
        return "I could not find relevant context in the knowledge base."

    if not settings.openai_api_key:
        joined = " ".join(c["chunk"] for c in citations)
        return f"Grounded response for '{query}': {joined[:900]}"

    client = OpenAI(api_key=settings.openai_api_key)
    context = _format_context(citations)
    prompt = (
        "You are a secure enterprise RAG assistant. Answer ONLY from provided context. "
        "If uncertain, say you do not have enough context. Keep answer concise.\n\n"
        f"Question: {query}\n\n"
        f"Context:\n{context}"
    )
    response = client.responses.create(
        model=settings.openai_model,
        input=prompt,
        temperature=0.2,
    )
    return response.output_text.strip()
