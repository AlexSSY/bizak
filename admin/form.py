from dataclasses import dataclass, asdict, field
from typing import Any, Optional, Callable
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from functools import wraps
from marshmallow import Schema

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


@dataclass
class TextareaWidget(Widget):
    template_name: str = '/widgets/textarea.html'
    class_: str = 'form-control'
    rows: int = 5


@dataclass
class CheckboxWidget(Widget):
    template_name: str = '/widgets/checkbox.html'
    class_: str = 'form-control'


FormFieldValidator = Callable[[str, Session], Optional[str]]


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
    widget: Widget
    type: str = 'text'
    value: str = ''
    name: Optional[str] = None
    required: bool = False
    validators: list[FormFieldValidator] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    shared: bool = True
    
    def __call__(self, templating: Jinja2Templates, old_values: dict[str, Any] = {}):
        template = templating.get_template(self.widget.template_name)
        context = asdict(self)
        context.update({
            'old_values': old_values
        })
        return template.render(context).strip()


@dataclass
class TextField(FormField):
    widget: Widget = field(default_factory=TextWidget)


@dataclass
class PasswordField(FormField):
    type: str = 'password'
    shared: bool = False
    widget: Widget = field(default_factory=TextWidget)


@dataclass
class BooleanField(FormField):
    value: bool = False
    type: str = 'checkbox'
    widget: Widget = field(default_factory=CheckboxWidget)


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
        schema: Schema = None

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
