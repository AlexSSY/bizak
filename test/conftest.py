import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.db import Base
from app.model import User


DB_FILE_NAME = '/test.sqlite3'
engine = create_engine(f'sqlite://{DB_FILE_NAME}')
SessionLocal: Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def db_prep():
    db_file_path  = DB_FILE_NAME
    
    if os.path.exists(db_file_path):
        os.remove(db_file_path)

    Base.metadata.create_all(bind=engine)

db_prep()

@pytest.fixture
def fake_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
