# app/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use DATABASE_URL env var if present, else default to local sqlite file
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")

# For SQLite we must pass check_same_thread=False when using the dev server
connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}

# create engine and session factory
engine = create_engine(DB_URL, echo=False, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base class for models
Base = declarative_base()
