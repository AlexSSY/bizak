from typing import Type, Optional, Literal
from sqlalchemy import Column, Integer, String
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Query, Session
from fastapi import Request
from admin.model import ModelAdmin, ModelAdminRegistry

from db import Base, create_all_tables, SessionLocal


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(length=100), unique=True)
    password = Column(String(length=200))


class UserAdmin(ModelAdmin):
    def get_id_display(self, obj):
        return obj.id
    get_id_display.display = 'ID'

    def get_username_display(self, obj):
        return obj.username.upper()

    def get_custom_display(self, obj):
        return f'custom field value for class: "{obj.__class__.__name__}"'
    get_custom_display.display = 'Custom'
    
    list_display = ['id', 'username', 'password', 'custom']


if __name__ == '__main__':
    from pprint import pprint
    create_all_tables()
    ModelAdminRegistry.register(User, UserAdmin)

    with SessionLocal() as session:
        pprint(ModelAdminRegistry.get_instance(User).index_view(None, session))
