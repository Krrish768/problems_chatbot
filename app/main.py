# app/main.py
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from .seed_db import init_db

app = FastAPI(title="Problems Chatbot API")

@app.on_event("startup")
def startup():
    # create tables and seed data
    init_db()

class ChatRequest(BaseModel):
    user_message: str
    user_email: EmailStr | None = None

class ChatResponse(BaseModel):
    reply: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Temporary echo — we will replace this with actual retrieval logic next
    return {"reply": f"you said: {req.user_message}"}
