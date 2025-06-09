from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from fastapi import Request
from admin.model import ModelAdmin, ModelAdminRegistry, display

from .db import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(length=100), unique=True)
    password = Column(String(length=200))


class UserAdmin(ModelAdmin):
    @display(display='ID')
    def get_id_display(self, obj):
        return obj.id

    @display(display='UserName')
    def get_username_display(self, obj):
        return obj.username

    @display(display='Custom')
    def get_custom_display(self, obj):
        return f'custom field value for class: "{obj.__class__.__name__}"'
    
    list_display = ['id', 'username', 'password', 'custom']
    search_columns = ['username']


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


ModelAdminRegistry.register(User, UserAdmin)
ModelAdminRegistry.register(Flower, FlowerAdmin)
