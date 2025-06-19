from sqlalchemy.orm import ColumnProperty
from wtforms_sqlalchemy.orm import ModelConverter

from .validators import Unique


class MyModelConverter(ModelConverter):
    def convert(self, model, mapper, prop, field_args, db_session=None):
        # * вешаем всем полям формы css класс "form-control"
        # ! HARDCODED ИСПРАВИТЬ!
        if not field_args:
            field_args = {}
        render_kw = field_args.setdefault("render_kw", {})
        render_kw.setdefault("class", "form-control")

        field = super().convert(model, mapper, prop, field_args, db_session=db_session)

        if isinstance(prop, ColumnProperty):
            column = prop.columns[0]

            # * Вот здесь мы добавляем кастомный валидатор на уникальность если поле
            # * задекларированно как уникальное
            if getattr(column, 'unique', False):
                validators = field.kwargs.get('validators', [])
                if not any(isinstance(v, Unique) for v in validators):
                    validators.insert(0, Unique(model=model, field=column.name, session=db_session))
                    field.kwargs['validators'] = validators

        return field
