from typing import Optional
from types import MethodType
from sqlalchemy import inspect
from sqlalchemy.orm import Query
from sqlalchemy.orm import Session
from fastapi import Request
from .types import SQLAlchemyModel
from .index_list import IndexList


class ModelAdmin:
    def __init__(self, model: SQLAlchemyModel):
        self.model = model
        self.name = self.__class__.__name__

    def get_queryset(self, request: Request, session: Session) -> Query:
        return session.query(self.model)
    
    def get_name(self) -> str:
        return self.model.__class__.__name__
    
    def get_name_plural(self) -> str:
        return self.model.__class__.__name__
    
    def _display_columns(self) -> list[str]:
        if isinstance(self.list_display, str):
            if self.list_display != '__all__':
                error_msg = f'The list_display attribute of a {self.name} - invalid'
                raise ValueError(error_msg)
            else:
                inspected_model = inspect(self.model)
                sql_columns = inspected_model.columns
                return sql_columns

        elif isinstance(self.list_display, list):
            if len(self.list_display) == 0:
                error_msg = f'The list_display attribute of a {self.name} - empty list'
                raise ValueError(error_msg)
            else:
                return self.list_display
                
        else:
            error_msg = f'The list_display attribute of a {self.name} must return list or str'
            raise ValueError(error_msg)
    
    def index_view(self, request: Request, session: Session) -> dict:
        ctx_columns = list()

        columns_to_display = self._display_columns()

        def display_methods():
            for column in columns_to_display:
                column_display_method = getattr(self, f'get_{column}_display', None)
                display = getattr(column_display_method, 'display', None)
                if column_display_method:
                    yield display or column
                else:
                    if column in sql_columns:
                        def display_method(self, obj):
                            return getattr(obj, 'column')
                        display_method.display = column
                        bound_display_method = MethodType(display_method, self)
                        setattr(self, f'get_{column}_display', bound_display_method)
                        yield column
                    else:
                        error_msg = f'column {column} not in DB table.'
                        raise ValueError(error_msg)
                
        for column in sql_columns:
            pass
            
        index_list = IndexList(request, self.model, self.get_queryset(request, session), [])
        
        return {
            'columns': ctx_columns,
            '_columns': [
                {'db_name': 'id', 'display': 'ID'},
                {'db_name': None, 'display': 'custom'},
            ],
            '_records': [
                [1, 'spagetti'],
                [2, 'buret'],
            ],
            'records': index_list.get_context()['records']
        }

    
    list_display = '__all__'
    fields = '__all__'
    exclude_fields = []


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
