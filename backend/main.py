from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

# Adjust if your Ollama URL or model is different
OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "llama3.1"

app = FastAPI()

# Allow your Next.js frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # later: replace "*" with your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "FastAPI HR backend is running on 8000"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Call Ollama chat API
    r = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": "You are Duke, a friendly HR assistant.",
                },
                {
                    "role": "user",
                    "content": req.message,
                },
            ],
            "stream": False,
        },
    )
    r.raise_for_status()
    data = r.json()
    reply_text = data["message"]["content"]
    return ChatResponse(reply=reply_text)
