from typing import Optional, Protocol
from types import MethodType
from sqlalchemy import inspect
from sqlalchemy.orm import Query
from sqlalchemy.orm import Session
from fastapi import Request

from .types import SQLAlchemyModel
from .index_list import index_list


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
    
    def _sql_columns(self) -> list[str]:
        inspected_model = inspect(self.model)
        return list([k.name for k in inspected_model.columns])
    
    def _display_columns(self) -> list[str]:
        """Returns actual list of list_display"""

        if isinstance(self.list_display, str):
            if self.list_display != '__all__':
                error_msg = f'The list_display attribute of a {self.name} - invalid'
                raise ValueError(error_msg)
            
            else:
                return self._sql_columns()

        elif isinstance(self.list_display, list):
            if len(self.list_display) == 0:
                error_msg = f'The list_display attribute of a {self.name} - empty list'
                raise ValueError(error_msg)
            else:
                return self.list_display
                
        else:
            error_msg = f'The list_display attribute of a {self.name} must return list or str'
            raise ValueError(error_msg)
    
    def _generate_display_func(self, column):
        def generated_display_method(self, obj):
                return getattr(obj, f'{column}')
        yield generated_display_method


    def _display_methods(self):
        display_methods = []
        sql_columns = self._sql_columns()
        display_columns = self._display_columns()
        search_columns = []
        
        for column in display_columns:
            display_method = getattr(self, f'get_{column}_display', None)

            if display_method:
                if not hasattr(display_method.__func__, 'display'):
                    setattr(display_method.__func__, 'display', column)
                display_methods.append(display_method)
            elif column in sql_columns:
                generated_display_func = next(self._generate_display_func(column))
                generated_display_func.display = column
                bound_generated_display_method = MethodType(generated_display_func, self)
                setattr(self, f'get_{column}_display', bound_generated_display_method)
                display_methods.append(bound_generated_display_method)
            else:
                error_msg = f'column {column} not in DB table.'
                raise ValueError(error_msg)
                
        return display_methods
    
    
    def index_view(self, request: Request, session: Session) -> dict:
        display_methods = self._display_methods()

        offset = request.query_params.get('offset', default=0)
        limit = request.query_params.get('limit', default=8)
        search = request.query_params.get('search', default=None)

        db_records = index_list(
            request=request,
            model=self.model,
            queryset=self.get_queryset(request, session),
            column_names=self.search_columns,
            offset=offset,
            limit=limit,
            search=search
        )
        records = []
        for db_record in db_records:
            values = []
            for display_method in display_methods:
                values.append(display_method(db_record))
            records.append(values)

        return {
            'columns': list([c.display for c in display_methods]),
            'records': records,
        }
    
    list_display = '__all__'
    fields = '__all__'
    exclude_fields = []
    search_columns = []


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
    
    @classmethod
    def get_instance_by(cls, model_class_name: str) -> ModelAdmin:
        result = tuple([(k, v) for k, v in cls.admin_model_storage.items() if k.__name__ == model_class_name])
        if not result:
            raise ValueError(f'model: {model_class_name} is not registered in AdminModelRegistry')
        model_class = result[0][0]
        model_admin_class = result[0][1]
        return model_admin_class(model_class)
