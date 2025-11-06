# models.py
from sqlalchemy import Column, Integer, Text, String, TIMESTAMP, func
from .db import Base

class FAQ(Base):
    __tablename__ = "faqs"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    tags = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

class PendingQuery(Base):
    __tablename__ = "pending_queries"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=True)
    user_message = Column(Text, nullable=False)
    status = Column(String, default="open")   # open | answered | ignored
    submitted_at = Column(TIMESTAMP, server_default=func.now())
