from dataclasses import dataclass, asdict, field
from typing import Any, Optional, Callable
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from functools import wraps
from marshmallow import Schema, ValidationError
from .types import SQLAlchemyModel


def get_model_fields(model_cls: SQLAlchemyModel):
    fields = []
    for column in model_cls.__table__.columns:
        if column.primary_key and column.autoincrement:
            continue  # не отображаем id
        field = {
            "name": column.name,
            "nullable": column.nullable,
            "type": column.type.python_type.__name__,  # str, int, etc.
            "default": column.default.arg if column.default else None,
        }
        fields.append(field)
    return fields


@dataclass
class Widget:
    template_name: str
    class_: str = ''


@dataclass
class TextWidget(Widget):
    template_name: str = '/widgets/input.html'
    class_: str = 'form-control'


FormFieldValidator = Callable[[str, Session], Optional[str]]


def form_field_validates(*field_names):
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
    type: str
    widget: Widget
    value: str = ''
    name: Optional[str] = None
    required: bool = False
    validators: list[FormFieldValidator] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class FormMeta(type):
    def __new__(cls, name, bases, namespace):
        form_fields = []
        for key, val in namespace.items():
            if key.startswith('__'):
                continue
            if isinstance(val, FormField):
                if val.name == None:
                    val.name = key
                form_fields.append(val)
        namespace['form_fields'] = form_fields
        return super().__new__(cls, name, bases, namespace)


class Form(metaclass=FormMeta):
    def __init__(self):
        self.valid = True

    class Meta:
        model: SQLAlchemyModel = None
        schema: Schema = None

    def save(self, data: dict[str, Any], session: Session):
        ...

    def validate(self, form_data: dict[str, Any], session: Session):
        self.cleaned_data = {}

        for field in self.form_fields:
            field_value = form_data.get(field.name)
            for validator in field.validators:
                validation_error = validator(field_value, session)
                if validation_error:
                    self.valid = False
                    field.errors.append(validation_error)
            self.cleaned_data[field.name] = field_value


    def fields_html(self, templating: Jinja2Templates, old_values: dict[str, Any] = {}) -> list[str]:
        fields_html = []

        for field in self.form_fields:
            template = templating.get_template(field.widget.template_name)
            context = asdict(field)
            context.update({
                'old_values': old_values
            })
            html = template.render(context)
            fields_html.append(html.strip())

        return fields_html
