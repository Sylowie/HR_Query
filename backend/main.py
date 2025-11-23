from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

import json
import numpy as np
import requests
import re  # <-- needed for regex formatting

from ollama_api.ollama_prompt import query_ollama  # your HR prompt wrapper

# ---- Embedding / Ollama config ----
EMBED_MODEL = "nomic-embed-text"
OLLAMA_URL = "http://localhost:11434"

app = FastAPI()

# CORS so your frontend can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # TODO: lock this down in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Load precomputed chunks index on startup ----
with open("data/chunks.json", "r", encoding="utf-8") as f:
    CHUNKS = json.load(f)

# All embeddings in a single matrix for fast similarity search
EMBS = np.array([c["embedding"] for c in CHUNKS])


def get_query_embedding(text: str) -> np.ndarray:
    """
    Call Ollama's embedding API to get an embedding vector for the query text.
    """
    r = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
    )
    r.raise_for_status()
    return np.array(r.json()["embedding"])


def retrieve_chunks(
    query: str,
    top_k: int = 4,
    allowed_docs: Optional[List[str]] = None,
):
    """
    Retrieve the top_k most relevant chunks from the index for a given query,
    optionally restricted to certain doc_ids.
    """
    q_emb = get_query_embedding(query)

    if allowed_docs:
        idxs = [i for i, c in enumerate(CHUNKS) if c["doc_id"] in allowed_docs]
        if not idxs:
            return []
        embs = EMBS[idxs]
    else:
        idxs = list(range(len(CHUNKS)))
        embs = EMBS

    # Cosine similarity between query embedding and each chunk embedding
    sims = embs @ q_emb / (
        np.linalg.norm(embs, axis=1) * np.linalg.norm(q_emb) + 1e-10
    )

    top_idx = np.argsort(-sims)[:top_k]
    return [CHUNKS[idxs[i]] for i in top_idx]


def format_llm_reply(text: str) -> str:
    """
    Post-process the LLM reply to make it easier to read:

    - Put bold headings like **Something** on their own lines.
    - Put each bullet (• or *) on its own line.
    - Collapse excessive blank lines.
    """
    # Make sure we are dealing with a string
    if not isinstance(text, str):
        text = str(text)

    if not text:
        return text

    # 1) Headings: bold phrases starting with a capital letter → separate block
    #    e.g. "**Supporting Individual Employees...**" or "**Summary**"
    def heading_repl(match):
        heading = match.group(1).strip()
        return f"\n\n**{heading}**\n\n"

    # Only treat bold segments that look like headings (start with capital)
    text = re.sub(r"\*\*([A-Z][^*]+?)\*\*", heading_repl, text)

    # 2) Ensure bullets are on their own line
    # "* text" or "• text" → newline before them
    text = re.sub(r"\s*\*\s+", r"\n* ", text)   # markdown bullets
    text = re.sub(r"\s*•\s+", r"\n• ", text)    # unicode bullets

    # 3) Collapse 3+ newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


class ChatRequest(BaseModel):
    """
    Request body for /chat.
    """
    message: str
    doc_ids: Optional[List[str]] = None  # which PDFs to search in (optional)


class ChatResponse(BaseModel):
    """
    Response body for /chat.
    """
    reply: str


@app.get("/")
def read_root():
    return {"status": "ok", "message": "FastAPI HR backend is running on 8000"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Main chat endpoint:
      1. Retrieve relevant chunks (RAG).
      2. Build database_context from chunk texts.
      3. Call Ollama with HR prompt.
      4. Post-process reply for readability.
    """
    # 1) Retrieve relevant chunks
    chunks = retrieve_chunks(
        query=req.message,
        top_k=4,
        allowed_docs=req.doc_ids,
    )

    if chunks:
        db_context = "\n\n---\n\n".join(c["text"] for c in chunks)
    else:
        db_context = ""

    # 2) Call Ollama via your helper
    reply_text = query_ollama(
        database_context=db_context,
        user_query=req.message,
    )

    # 3) Clean up formatting for UI
    reply_text = format_llm_reply(reply_text)

    return ChatResponse(reply=reply_text)
