from contextlib import asynccontextmanager
from typing import Type
from fastapi import Request, FastAPI, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from wtforms import Form, ValidationError, validators, StringField, IntegerField, SelectField
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapper, DeclarativeBase, Session, DeclarativeMeta


def Unique(model, field_name: str, session_getter):
    """
    Проверяет, что значение уникально в модели.
    
    :param model: SQLAlchemy модель (например, User)
    :param field_name: строка, имя столбца (например, 'email')
    :param session_getter: функция, возвращающая активную сессию (Session)
    """
    def _validate(form, field):
        session = session_getter()
        value = field.data

        if value is None:
            return  # можно не проверять null

        column = getattr(model, field_name)
        exists = session.query(model).filter(column == value).first()

        if exists:
            raise ValidationError(f"{field.label.text} должен быть уникальным.")

    return _validate


def _resolve_model(table, base: DeclarativeMeta) -> type:
    """
    Найти модель, связанную с таблицей, среди потомков DeclarativeBase.
    
    :param table: sqlalchemy.Table
    :param base: DeclarativeBase или declarative_base()
    """
    for mapper in base.registry.mappers:
        cls = mapper.class_
        if hasattr(cls, '__table__') and cls.__table__ == table:
            return cls
    raise ValueError(f"Не найдена модель для таблицы '{table.name}'")


def nullable_int(val):
    return int(val) if val not in ("", None) else None


def form_for_model(model: Type[DeclarativeBase], base: DeclarativeMeta, session: Session) -> Type[Form]:
    mapper: Mapper = model.__mapper__
    fields = {}

    for column in mapper.columns:
        name = column.key
        type_ = column.type
        is_required = not column.nullable and not column.default and not column.primary_key
        is_unique = column.unique or False

        # Пропустим id-поле
        if column.primary_key:
            continue

        _validators = []
        if is_required:
            _validators.append(validators.DataRequired())

        if is_unique:
            _validators.append(Unique(model, name, lambda: session))

        if isinstance(type_, String):
            if type_.length:
                _validators.append(validators.Length(max=type_.length))
            fields[name] = StringField(name.capitalize(), validators=_validators)

        elif isinstance(type_, Integer):
            fk = next(iter(column.foreign_keys), None)
            if fk:
                # Внешний ключ → SelectField
                target_table = fk.column.table
                target_model = _resolve_model(target_table, base)

                # Создаём choices из target_model
                # session = session_getter()
                rows = session.query(target_model).all()
                choices = [('', '---')] + [(getattr(row, fk.column.name), str(row)) for row in rows]

                fields[name] = SelectField(name.capitalize(), choices=choices, coerce=nullable_int, validators=_validators)
            else:
                fields[name] = IntegerField(name.capitalize(), validators=_validators)

        # * Можно добавить больше типов (Boolean, Float и т.д.)

    return type(f"{model.__name__}Form", (Form,), fields)
