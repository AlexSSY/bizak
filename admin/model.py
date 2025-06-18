from types import MethodType
from typing import Dict, List, Tuple, Type
from sqlalchemy import inspect
from sqlalchemy.orm import Query
from sqlalchemy.orm import Session
from fastapi import Request
from fastapi.templating import Jinja2Templates
import functools
import json

from .types import SQLAlchemyModel
from .index_list import index_list, parse_filters


class RecordValues(list):
    ...


class ModelAdmin:
    list_display = '__all__'
    fields = '__all__'
    exclude_fields = []
    search_columns = []

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
        """
        Формирует:
        Методы возвращающий значание для колонки (Column) +
        описание некоторых свойств отобрадения
        """
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
    
    
    def index_view(self, templating: Jinja2Templates, request: Request, session: Session) -> dict:
        """Render a html page list of records"""
        
        display_methods = self._display_methods()

        offset = request.query_params.get('offset', default=0)
        limit = request.query_params.get('limit', default=1000)
        limit = max(1, int(limit))
        search = request.query_params.get('search', default=None)
        order = request.query_params.get('order', default=None)
        order_type = request.query_params.get('order_type', default='asc')
        filters = parse_filters(request=request)

        db_records = index_list(
            request=request,
            model=self.model,
            queryset=self.get_queryset(request, session),
            search_column_names=self.search_columns,
            offset=offset,
            limit=limit,
            search=search,
            order=order,
            order_type=order_type,
            filters=filters
        )
        records = list()
        for db_record in db_records:
            values = RecordValues()
            for display_method in display_methods:
                values.append(display_method(db_record))
            setattr(values, 'ids', f'{db_record.id}')
            setattr(values, 'pks', json.dumps({'id': db_record.id}))
            records.append(values)

        context= {
            'columns': list([c.display for c in display_methods]),
            'records': records,
            'model': self.model.__name__.capitalize()
        }

        return templating.TemplateResponse(request, 'records.html', context)


def display(**parameters):
    """Decorator for custom fields"""
    def decorator(fn):
        # Назначаем кастомные атрибуты функции
        for key, val in parameters.items():
                setattr(fn, key, val)

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return decorator
