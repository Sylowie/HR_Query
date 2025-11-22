from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ollama_api.ollama_prompt import query_ollama 


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # later: lock this to your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str                      # user question
    context: str | None = None        # optional DB context from your RAG step


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
def read_root():
    return {"status": "ok", "message": "FastAPI HR backend is running on 8000"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Here you decide what context to pass in.
    # For now: whatever frontend / RAG layer sends in `req.context` (or empty string).
    db_context = req.context or ""

    reply_text = query_ollama(
        database_context=db_context,
        user_query=req.message,
    )

    return ChatResponse(reply=reply_text)
