from __future__ import annotations

from typing import Any, Dict, List
from app.services.rag.retriever import RetrievedChunk, retrieve_chunks
from app.services.llm.groq_client import generate_response  # we'll define this next


def format_context(chunks):
    context = "\n\n".join(
        f"[Source: {c.source} | score: {c.similarity:.2f}]\n{c.content}"
        for c in chunks
    )
    return context


def answer_with_rag(query: str, chat_history: List[Dict[str, Any]] = None):
    # 1. Retrieve relevant chunks
    chunks = retrieve_chunks(
        query=query,
        top_k=5,
        min_similarity=0.65,
    )

    # 2. Build context
    context = format_context(chunks)

    # 3. Build chat memory
    history_text = ""
    if chat_history:
        for msg in chat_history[-6:]:
            role = msg["role"]
            content = msg["content"]
            history_text += f"{role.upper()}: {content}\n"

    # 4. Final prompt
    prompt = f"""
You are a helpful AI assistant for a website chatbot.

Use only the CONTEXT below.
If the answer is not in the context, say you do not know.

CONTEXT:
{context}

CHAT HISTORY:
{history_text}

USER QUESTION:
{query}

Answer clearly and concisely.
"""

    # 5. LLM call (Groq)
    response = generate_response(prompt)

    return response, chunks

def format_context(chunks: List[RetrievedChunk]) -> str:
    if not chunks:
        return ""

    parts = []
    for i, chunk in enumerate(chunks, start=1):
        section = ""
        if chunk.metadata and chunk.metadata.get("section"):
            section = f" | Section: {chunk.metadata['section']}"

        parts.append(
            f"[Chunk {i}{section} | Source: {chunk.source} | Score: {chunk.similarity:.4f}]\n"
            f"{chunk.content}"
        )

    return "\n\n---\n\n".join(parts)


def retrieve_for_query(query: str, top_k: int = 5, min_similarity: float = 0.65):
    chunks = retrieve_chunks(
    query=query,
    top_k=top_k,
    min_similarity=min_similarity,
)

    return {
        "query": query,
        "chunks": chunks,
        "context": format_context(chunks),
    }