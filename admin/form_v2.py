from typing import Callable, Any, Optional, Dict, AnyStr
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase

from .base_v2 import Field


__all__ = ['BaseForm', 'Form']


SAModel = DeclarativeBase


class DeclarativeFormMeta(type):
    """Collect Fields declared on the base classes."""

    def __new__(mcs, name, bases, attrs):
        # Collect fields from current class and remove them from attrs.
        attrs["declared_fields"] = {
            key: attrs.pop(key)
            for key, value in list(attrs.items())
            if isinstance(value, Field)
        }

        # When `field.name` is none or empty-string - assign field.name attribute from 
        # attr_name where (attr_name = Field(...))
        for attr_name, field in attrs['declared_fields'].items():
            if not field.name:
                field.name = attr_name

        new_class = super().__new__(mcs, name, bases, attrs)

        # Walk through the MRO.
        declared_fields = {}
        for base in reversed(new_class.__mro__):
            # Collect fields from base class.
            if hasattr(base, "declared_fields"):
                declared_fields.update(base.declared_fields)

            # Field shadowing.
            for attr, value in base.__dict__.items():
                if value is None and attr in declared_fields:
                    declared_fields.pop(attr)

        new_class.base_fields = declared_fields
        new_class.declared_fields = declared_fields

        return new_class


class BaseForm:
    '''
    Класс формы (обязанности):
    1. только отрисовка
    2. только валидация (не БД)
    '''

    def __init__(self, data: Dict, db: Session):
        self._data = data
        self._cleaned_data = {}
        self._errors = {}
        self._db = db

    def is_valid(self) -> bool:
        self.cleaned_data = {}
        self.errors = {}
        self.validate()
        return not self.errors

    def validate(self):
        '''
        Собирает информацию о ошибках перебирая каждое поле и запуская по очереди
        их валидаторы. Ошибки сохраняются в self.errors
        '''

        for field in self.declared_fields.items():
            for validator in field.validators:
                field_name = field.name
                field_value = self.data.get(field.name)
                try:
                    message = validator(self, field_name, field_value)
                    if message:
                        self.add_error(field_name, message)
                except Exception as e:
                        self.add_error(field_name, str(e))


    def add_error(self, field_name: Optional[str], message: str):
        '''
        Добавить ошибку к полю "field" если переданно None
        ошибка добавляется под спец. ключом который интерпритируется
        как (глобальная ошибка формы)
        '''
        self.errors.setdefault(field_name if field_name else '__', []).append(message)


class Form(BaseForm, metaclass=DeclarativeFormMeta):
    ...
