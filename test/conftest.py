import os
import pytest
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from admin.model import ModelAdmin, ModelAdminRegistry
from datetime import datetime
from fastapi.testclient import TestClient
from .db import Base, SessionLocal, engine


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)


class Flower(Base, TimestampMixin):
    __tablename__ = 'flowers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    color = Column(String)


class FlowerAdmin(ModelAdmin):
    search_columns = ['name', 'color']


ModelAdminRegistry.register(Flower, FlowerAdmin)


def db_prep():
    # db_file_path  = DB_FILE_NAME
    
    # if os.path.exists(db_file_path):
    #     os.remove(db_file_path)

    # Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
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

db_prep()

@pytest.fixture(scope="function")
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(db: Session):
    def override_get_db():
        yield db
    app.dependency_overrides[app.get_db] = override_get_db
    return TestClient(app)
