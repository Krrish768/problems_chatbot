# db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use a MySQL URL in production via ENV: DATABASE_URL
# Example: mysql+pymysql://chatadmin:MyStrongPass123@localhost:3306/chatbot
DB_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://chatadmin:MyStrongPass123@localhost:3306/chatbot"
)

# For sqlite you might need connect_args, but for MySQL leave empty
connect_args = {}

engine = create_engine(DB_URL, echo=False, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
