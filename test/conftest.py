import os
import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from .db import SessionLocal, engine
from app.db import get_db
from app.model import Flower, Base
from app.server import app


def db_prep():
    # db_file_path  = DB_FILE_NAME
    
    # if os.path.exists(db_file_path):
    #     os.remove(db_file_path)

    # Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        # 12 records
        session.add(Flower(name='Роза', color='красный'))
        session.add(Flower(name='Лилия', color='жовтый'))
        session.add(Flower(name='Ласточкина трава', color='белый'))
        session.add(Flower(name='Крижовник', color='черный'))
        session.add(Flower(name='Сирень', color='синий'))
        session.add(Flower(name='Мышехвост', color='белый'))
        session.add(Flower(name='Двоегрот', color='красный'))
        session.add(Flower(name='Себачая петрушка', color='белый'))
        session.add(Flower(name='Драконий корень', color='красный'))
        session.add(Flower(name='Омела', color='белый'))
        session.add(Flower(name='Хмель', color='белый'))
        session.add(Flower(name='Чертополох', color='желтый'))
        session.commit()


@pytest.fixture(scope="function")
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db_prep()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db: Session):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
