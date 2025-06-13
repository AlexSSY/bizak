from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from admin.model import ModelAdmin, ModelAdminRegistry, display

from .db import Base, get_db


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(length=100), unique=True, nullable=False, doc='Unique username')
    password = Column(String(length=200))
    posts = relationship('Post', back_populates='author')

    def __str__(self):
        return self.username


class Post(Base, TimestampMixin):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(length=100), unique=True)
    body = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))
    author = relationship('User', back_populates='posts')


class Comment(Base, TimestampMixin):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(length=100), unique=True)
    body = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('posts.id'))


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


class Flower(Base, TimestampMixin):
    __tablename__ = 'flowers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    color = Column(String)


class FlowerAdmin(ModelAdmin):
    search_columns = ['name', 'color']


class PostAdmin(ModelAdmin):
    @display(display='Author')
    def get_user_id_display(self, obj):
        return obj.author


ModelAdminRegistry.register(User, UserAdmin)
ModelAdminRegistry.register(Flower, FlowerAdmin)
ModelAdminRegistry.register(Post, PostAdmin)
