
from sqlalchemy import Column, Integer, String
from fastapi import Request
from admin.model import ModelAdmin, ModelAdminRegistry

from .db import Base, create_all_tables


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


ModelAdminRegistry.register(User, UserAdmin)
