# main.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from .seed_db import init_db
from .db import SessionLocal
from .models import FAQ, PendingQuery
import re
import os

app = FastAPI(title="Simple FAQ Chatbot")

@app.on_event("startup")
def startup():
    init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Client sends only 'query' when chatting (UI requirement: only ask query)
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    reply: str
    found: bool
    pending_id: int | None = None
    need_email: bool | None = None

class SubmitEmailRequest(BaseModel):
    pending_id: int
    email: EmailStr

# Admin simple auth
class AdminAuth(BaseModel):
    admin_password: str

class AnswerRequest(AdminAuth):
    query_id: int
    answer: str

STOPWORDS = {
    "the","is","a","an","and","or","of","to","how","do","what","can","i","my","you","we","in","on","for","are","be","it","will","did","was"
}

def extract_keywords(text: str):
    words = re.findall(r"\w+", text.lower())
    keywords = [w for w in words if len(w) > 2 and w not in STOPWORDS]
    return keywords

def verify_admin(pw: str):
    real = os.getenv("ADMIN_PASSWORD", "adminpass")
    return pw == real

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    msg = req.query.strip()
    if not msg:
        return {"reply": "Please send a question.", "found": False, "pending_id": None, "need_email": False}

    # 1) exact match
    faq = db.query(FAQ).filter(FAQ.question.ilike(msg)).first()
    # 2) contains
    if not faq:
        faq = db.query(FAQ).filter(FAQ.question.ilike(f"%{msg}%")).first()
    # 3) tag match via keywords
    if not faq:
        keywords = extract_keywords(msg)
        for k in keywords:
            faq = db.query(FAQ).filter(FAQ.tags.ilike(f"%{k}%")).first()
            if faq:
                break
    # 4) best overlap with question keywords
    if not faq:
        keywords = extract_keywords(msg)
        if keywords:
            faqs = db.query(FAQ).all()
            best = None
            best_score = 0
            for f in faqs:
                q_keywords = extract_keywords(f.question)
                score = len(set(keywords) & set(q_keywords))
                if score > best_score:
                    best_score = score
                    best = f
            if best and best_score >= 1:
                faq = best

    if faq:
        return {"reply": faq.answer, "found": True, "pending_id": None, "need_email": False}

    # not found -> create pending query WITHOUT email, return pending_id and ask for email
    pq = PendingQuery(user_email=None, user_message=msg, status="open")
    db.add(pq)
    db.commit()
    db.refresh(pq)
    return {
        "reply": "I couldn't find an answer. Please provide your email using /chat/submit_email with the returned pending_id so we can notify you when it's answered.",
        "found": False,
        "pending_id": pq.id,
        "need_email": True
    }

@app.post("/chat/submit_email")
def submit_email(req: SubmitEmailRequest, db: Session = Depends(get_db)):
    pq = db.query(PendingQuery).filter(PendingQuery.id == req.pending_id).first()
    if not pq:
        raise HTTPException(status_code=404, detail="Pending id not found")
    pq.user_email = req.email
    db.commit()
    return {"ok": True, "message": "Email saved. We'll notify when the query is answered."}

# --- Admin endpoints ---
@app.post("/admin/pending/list")
def admin_list(auth: AdminAuth, db: Session = Depends(get_db)):
    if not verify_admin(auth.admin_password):
        raise HTTPException(status_code=403, detail="Forbidden")
    rows = db.query(PendingQuery).order_by(PendingQuery.submitted_at.desc()).all()
    return [{"id": r.id, "user_email": r.user_email, "user_message": r.user_message, "status": r.status, "submitted_at": str(r.submitted_at)} for r in rows]

@app.post("/admin/pending/answer")
def admin_answer(req: AnswerRequest, db: Session = Depends(get_db)):
    if not verify_admin(req.admin_password):
        raise HTTPException(status_code=403, detail="Forbidden")
    pq = db.query(PendingQuery).filter(PendingQuery.id == req.query_id).first()
    if not pq:
        raise HTTPException(status_code=404, detail="Pending query not found")
    # add to FAQ
    faq = FAQ(question=pq.user_message, answer=req.answer, tags=None)
    db.add(faq)
    pq.status = "answered"
    db.commit()
    return {"ok": True, "message": "Saved answer and marked pending query as answered."}

@app.post("/admin/pending/delete")
def admin_delete(req: AnswerRequest, db: Session = Depends(get_db)):
    # reuse AnswerRequest to carry admin_password + query_id
    if not verify_admin(req.admin_password):
        raise HTTPException(status_code=403, detail="Forbidden")
    pq = db.query(PendingQuery).filter(PendingQuery.id == req.query_id).first()
    if not pq:
        raise HTTPException(status_code=404, detail="Pending query not found")
    db.delete(pq)
    db.commit()
    return {"ok": True, "message": "Pending query deleted."}
