from typing import Type, Optional, Literal
from sqlalchemy import Column, Integer, String
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Query, Session
from fastapi import Request

from db import Base, create_all_tables


SQLAlchemyModel = Type[Base]


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(length=100), unique=True)
    password = Column(String(length=200))


class AdminModel:
    def __init__(self, model: SQLAlchemyModel):
        self.model = model

    def get_queryset(self, request: Request, session: Session) -> Query:
        return session.query(self.model)
    
    def get_name(self) -> str:
        return self.model.__name__
    
    def get_name_plural(self) -> str:
        return self.model.__name__
    
    def get_list_display(self) -> Optional[list[str] | Literal['__all__']]:
        return '__all__'


admin_model_storage: dict[SQLAlchemyModel, AdminModel] = dict()


class AdminModelMetadata:
    pass


if __name__ == '__main__':
    create_all_tables()

    from pprint import pprint
    inspected_model = inspect(User)
    columns = inspected_model.columns

    for c in columns:
        pprint(c)
