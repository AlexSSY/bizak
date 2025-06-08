import os
import pytest
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base


DB_FILE_NAME = 'test.sqlite3'
engine = create_engine(f'sqlite:///{DB_FILE_NAME}')
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Flower(Base):
    __tablename__ = 'flowers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    color = Column(String)
    
    created_at = Column(DateTime)


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
