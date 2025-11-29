from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Generator
from pathlib import Path

DATABASE_URL = "sqlite:///./resources/db/cardiomaton_code.db"
RESOURCES_DIR = ...

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()