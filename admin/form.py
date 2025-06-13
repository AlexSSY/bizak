from dataclasses import dataclass, asdict, field
from typing import Any, Dict, Literal, Optional, Callable, Type
from fastapi import Request
from sqlalchemy import Column, Table
from sqlalchemy.orm import Session, class_mapper
from fastapi.templating import Jinja2Templates
from functools import wraps

from .types import SQLAlchemyModel


FormFieldValidator = Callable[[Any, str, Any, Session], Optional[str]]


def validates(*field_names):
    def decorator(fn):
        fn._validates_fields = field_names
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return decorator


Html = str


@dataclass
class FormField:
    label: str
    type: str
    value: str = None
    input_template: str = '/widgets/input.html'
    label_template: str = '/widgets/label.html'
    help_template: str = '/widgets/help.html'
    errors_template: str = '/widgets/errors.html'
    help: Optional[str] = None
    name: Optional[str] = None
    required: bool = False
    validators: list[FormFieldValidator] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    shared: bool = True
    
    def __call__(self, templating: Jinja2Templates, old_values: dict[str, Any] = {}) -> Dict[str, Html]:
        templates = {
            'input': templating.get_template(self.input_template),
            'label': templating.get_template(self.label_template),
            'help': templating.get_template(self.help_template),
            'errors': templating.get_template(self.errors_template),
        }

        context = asdict(self)
        context.update({
            'old_values': old_values
        })

        result = {k: v.render(context).strip() for k, v in templates.items()} 
        return result


@dataclass
class TextField(FormField):
    type: str = 'text'


@dataclass
class TextareaField(FormField):
    input_template: str = '/widgets/textarea.html'
    type: str = 'textarea'
    rows: int = 5


@dataclass
class IntegerField(FormField):
    type: str = 'number'


@dataclass
class PasswordField(FormField):
    type: str = 'password'
    shared: bool = False


@dataclass
class BooleanField(FormField):
    value: bool = False
    type: str = 'checkbox'
    input_template: str = '/widgets/checkbox.html'


@dataclass
class SelectField(FormField):
    value: str = ''
    type: str = 'select'
    items: list[tuple[int, str]] = field(default_factory=list)
    multi: bool = False
    input_template: str = '/widgets/select.html'


@dataclass
class DateTimeField(FormField):
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
        readonly_fields = []
        fields = '__all__'
        exclude = []

    def _clear_errors(self):
        for field in self.form_fields:
            field.errors.clear()

    def save(self, data: dict[str, Any], session: Session):
        self.validate(data, session)
        instance = self.Meta.model(**data)
        session.add(instance)
        session.commit()

    def validate(self, form_data: dict[str, Any], session: Session) -> bool:
        self.cleaned_data = {}
        self.valid = True  # Сброс перед валидацией

        self._clear_errors()
        for field in self.form_fields:
            field_value = form_data.get(field.name)

            for validator in field.validators:
                try:
                    validation_error = validator(self, field.name, field_value, session)
                except Exception as e:
                    # если вдруг валидатор падает, мы не ломаем всю валидацию
                    validation_error = str(e)

                if validation_error:
                    field.errors.append(validation_error)
                    self.valid = False

            self.cleaned_data[field.name] = field_value
        
        return self.valid

    def fields_html(self, templating: Jinja2Templates, old_values: dict[str, Any] = {}) -> list[str]:
        fields_html = []

        for field in self.form_fields:
            html = field(templating=templating, old_values=old_values)
            fields_html.append(html)

        return fields_html
    
    async def render_to_html(
            self,
            request: Request,
            templating: Jinja2Templates, 
            template_name: str,
            action: str = '/',
            method: str = 'post'
        ) -> Html:
        """This call methods renders form to html string"""
        template = templating.get_template(template_name)
        old_values = await request.form()
        context = {
            'request': request,
            'method': method,
            'action': action,
            'fields': self.fields_html(templating, old_values),
            'model': self.Meta.model.__name__,
        }
        return template.render(context)


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


def unique_db_validator(form: Form, key: str, value: Any, session: Session) -> Optional[str]:
    model = form.Meta.model
    column = getattr(model, key)
    if session.query(model).filter(column == value).first():
        return 'already exists'
    return None


def model_to_form(model_cls: SQLAlchemyModel, session: Session, readonly_fields: list[str] = []) -> Form:
    form_fields = []
    for column in model_cls.__table__.columns:
        if column.primary_key and column.autoincrement:
            continue
        if column.name in readonly_fields:
            continue
        field = FieldFactory.create(model_cls, column, session)
        if column.unique:
            field.validators.append(unique_db_validator)
        if column.doc:
            field.help = column.doc
        form_fields.append(field)

    form = Form()
    form.form_fields = form_fields
    form.Meta.model = model_cls
    return form
