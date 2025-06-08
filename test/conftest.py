import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.db import Base
from app.model import User


DB_FILE_NAME = 'test.sqlite3'
engine = create_engine(f'sqlite:///{DB_FILE_NAME}')
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def db_prep():
    db_file_path  = DB_FILE_NAME
    
    if os.path.exists(db_file_path):
        os.remove(db_file_path)

    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        for i in range(8):
            user = User(username=f"username_{i}", password=f"password_{i}")
            session.add(user)
        session.commit()

db_prep()

@pytest.fixture
def fake_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
