from dataclasses import dataclass, asdict, field
from typing import Any, Dict, Optional, Callable, Type
from sqlalchemy import Column, Table
from sqlalchemy.orm import Session, class_mapper
from fastapi.templating import Jinja2Templates
from functools import wraps

from .types import SQLAlchemyModel


FormFieldValidator = Callable[[Any, str, Session], Optional[str]]


def validates(*field_names):
    def decorator(fn):
        fn._validates_fields = field_names
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@dataclass
class FormField:
    label: str
    template: str
    type: str
    # value: str = ''
    help: Optional[str] = None
    name: Optional[str] = None
    required: bool = False
    validators: list[FormFieldValidator] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    shared: bool = True
    
    def __call__(self, templating: Jinja2Templates, old_values: dict[str, Any] = {}) -> Dict[str, str]:
        template = templating.get_template(self.template)
        context = asdict(self)
        context.update({
            'old_values': old_values
        })
        return template.render(context).strip()


@dataclass
class TextField(FormField):
    template: str = '/widgets/input.html'
    type: str = 'text'


@dataclass
class TextareaField(FormField):
    template: str = '/widgets/textarea.html'
    type: str = 'textarea'
    rows: int = 5


@dataclass
class IntegerField(FormField):
    template: str = '/widgets/input.html'
    type: str = 'number'


@dataclass
class PasswordField(FormField):
    type: str = 'password'
    shared: bool = False
    template: str = '/widgets/input.html'


@dataclass
class BooleanField(FormField):
    value: bool = False
    type: str = 'checkbox'
    template: str = '/widgets/checkbox.html'


@dataclass
class SelectField(FormField):
    value: str = ''
    type: str = 'select'
    items: list[tuple[int, str]] = field(default_factory=list)
    multi: bool = False
    template: str = '/widgets/select.html'


@dataclass
class DateTimeField(FormField):
    template: str = '/widgets/input.html'
    type: str = 'datetime-local'


class FormMeta(type):
    def __new__(cls, name, bases, namespace):
        # Собираем валидаторы полей
        form_field_validators = {}
        for key, val in namespace.items():
            if callable(val) and hasattr(val, '_validates_fields'):
                for validate_field_name in val._validates_fields:
                    form_field_validators.setdefault(validate_field_name, []).append(val)

        # Наследованные поля
        form_fields = []
        for base in bases:
            if hasattr(base, 'form_fields'):
                form_fields += base.form_fields

        # Новые поля
        for key, val in namespace.items():
            if isinstance(val, FormField):
                if val.name is None:
                    val.name = key
                val.validators.extend(form_field_validators.get(key, []))
                form_fields.append(val)

        namespace['form_fields'] = form_fields
        return super().__new__(cls, name, bases, namespace)


class Form(metaclass=FormMeta):
    def __init__(self):
        self.valid = True
        self._clear_errors()

    class Meta:
        model: SQLAlchemyModel = None

    def _clear_errors(self):
        for field in self.form_fields:
            field.errors.clear()

    def save(self, data: dict[str, Any], session: Session):
        instance = self.Meta.model(**data)
        session.add(instance)
        session.commit()

    def validate(self, form_data: dict[str, Any], session: Session) -> dict[str, Any]:
        self.cleaned_data = {}
        self.valid = True  # Сброс перед валидацией

        self._clear_errors()
        for field in self.form_fields:
            field_value = form_data.get(field.name)
        #     field.value = field_value  # сохраняем текущее значение, чтобы отрисовать обратно в форме
        #     field.errors.clear()       # очищаем предыдущие ошибки

            for validator in field.validators:
                try:
                    validation_error = validator(self, field_value, session)
                except Exception as e:
                    # если вдруг валидатор падает, мы не ломаем всю валидацию
                    validation_error = str(e)

                if validation_error:
                    field.errors.append(validation_error)
                    self.valid = False

            self.cleaned_data[field.name] = field_value
        
        return self.cleaned_data


    def fields_html(self, templating: Jinja2Templates, old_values: dict[str, Any] = {}) -> list[str]:
        fields_html = []

        for field in self.form_fields:
            fields_html.append(field(templating=templating, old_values=old_values))

        return fields_html


class FieldFactory:
    _registry = {
        'String': TextField,
        'Text': TextareaField,
        'Integer': IntegerField,
        'DateTime': DateTimeField,
    }

    @staticmethod
    def create(model_cls: SQLAlchemyModel, column: Column, session: Session) -> FormField:
        # 1. ForeignKey — создаём SelectField
        if column.foreign_keys:
            related_model = FieldFactory.resolve_related_model(model_cls, column.name)
            items = [(getattr(obj, 'id'), str(obj)) for obj in session.query(related_model).all()]
            return SelectField(
                name=column.name,
                label=column.name,
                required=not column.nullable,
                items=items
            )

        # 2. Простые типы — создаём по _registry
        type_name = column.type.__class__.__name__
        field_class = FieldFactory._registry.get(type_name, TextField)
        return field_class(
            name=column.name,
            label=column.name,
            required=not column.nullable,
        )

    def resolve_related_model(model_cls, field_name):
        mapper = class_mapper(model_cls)
        prop = mapper.get_property(field_name)
        
        if hasattr(prop, 'mapper'):  # relationship
            return prop.mapper.class_
        elif hasattr(prop, 'columns'):
            column = prop.columns[0]
            fk = list(column.foreign_keys)[0]
            related_table = fk.column.table
            
            # Используем способ через registry
            for m in model_cls.registry.mappers:
                if m.local_table is related_table:
                    return m.class_
        
        raise ValueError(f"Can't resolve related model for field '{field_name}'")


def model_to_form(model_cls: SQLAlchemyModel, session: Session) -> Form:
    form_fields = []
    for column in model_cls.__table__.columns:
        if column.primary_key and column.autoincrement:
            continue
        if column.name == 'created_at' or column.name == 'updated_at':
            continue
        field = FieldFactory.create(model_cls, column, session)
        form_fields.append(field)

    form = Form()
    form.form_fields = form_fields
    return form
