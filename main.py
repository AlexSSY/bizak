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


class ModelAdmin:
    def __init__(self, model: SQLAlchemyModel):
        self.model = model

    def get_queryset(self, request: Request, session: Session) -> Query:
        return session.query(self.model)
    
    def get_name(self) -> str:
        return self.model.__class__.__name__
    
    def get_name_plural(self) -> str:
        return self.model.__class__.__name__
    
    list_display = '__all__'


class ModelAdminRegistry:
    admin_model_storage: dict[SQLAlchemyModel, ModelAdmin] = dict()

    @classmethod
    def register(cls, model: SQLAlchemyModel, model_admin_class: ModelAdmin):
        cls.admin_model_storage[model] = model_admin_class

    @classmethod
    def get_instance(cls, model: SQLAlchemyModel) -> ModelAdmin:
        model_admin_class = cls.admin_model_storage.get(model)
        if model_admin_class == None:
            raise ValueError(f'model: {model} is not registered in AdminModelRegistry')
        return model_admin_class(model)


class UserAdmin(ModelAdmin):
    def get_id_display(self):
        return 'ID'
    
    list_display = ['id', 'username']


if __name__ == '__main__':
    from pprint import pprint
    create_all_tables()
    ModelAdminRegistry.register(User, UserAdmin)

    inspected_model = inspect(User)
    sql_columns = inspected_model.columns
    model_admin = ModelAdminRegistry.get_instance(User)
    model_admin_name = model_admin.__class__.__name__

    ma_list_display = model_admin.list_display

    ctx_column_names: list[str] = list()

    def customize_column(c):
        get_column_display = getattr(model_admin, f'get_{c.name}_display', None)
        if get_column_display:
            ctx_column_names.append(get_column_display())
        else:
            ctx_column_names.append(c.name)

    for c in sql_columns:
        # check if column name in the list_display
        if isinstance(ma_list_display, str):
            if ma_list_display != '__all__':
                error_msg = f'The get_list_display method of a {model_admin_name} - invalid'
                raise ValueError(error_msg)
            else:
                customize_column(c)
        elif isinstance(ma_list_display, list):
            if len(ma_list_display) == 0:
                error_msg = f'The get_list_display method of a {model_admin_name} returns empty list'
                raise ValueError(error_msg)
            else:
                if c.name not in ma_list_display:
                    continue
                customize_column(c)
        else:
            error_msg = f'The get_list_display method of a {model_admin_name} must return list or str'
            raise ValueError(error_msg)

    pprint(ctx_column_names)
