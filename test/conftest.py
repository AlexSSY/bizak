import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..main import User, Base
from db import SessionLocal


DB_FILE_NAME = 'test.sqlite3'


def db_prep():
    db_file_path  = f'/{DB_FILE_NAME}'
    
    if os.path.exists(db_file_path):
        os.remove(db_file_path)

    engine = create_engine(f'sqlite://{db_file_path}')
    global SessionLocal
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)


@pytest.fixture(scope='session', autouse=True)
def fake_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()