# seed_db.py
from .db import Base, engine, SessionLocal
from .models import FAQ

def init_db():
    # create tables if not exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Only seed if table empty
        if not db.query(FAQ).first():
            sample = []
            for i in range(1, 101):
                q = f"What is sample question number {i}?"
                a = f"This is sample answer number {i}. Use it as placeholder content."
                tags = "sample,seed,example"
                sample.append(FAQ(question=q, answer=a, tags=tags))
            db.add_all(sample)
            db.commit()
    finally:
        db.close()
