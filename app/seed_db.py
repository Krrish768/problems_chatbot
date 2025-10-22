# app/seed_db.py
from .db import Base, engine, SessionLocal
from .models import FAQ

def init_db():
    # create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # if no FAQ exists, seed sample rows
        if not db.query(FAQ).first():
            sample = [
                FAQ(
                    question="How do I reset my password?",
                    answer="Go to Settings → Account → Click 'Reset Password' and follow the steps.",
                    tags="account,password"
                ),
                FAQ(
                    question="How to export data?",
                    answer="Open Reports → Export → choose CSV and click Export.",
                    tags="export,csv"
                ),
            ]
            db.add_all(sample)
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("DB initialized and seeded.")
