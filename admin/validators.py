from wtforms.validators import StopValidation


class Unique:
    def __init__(self, model, field, session, message="Must be unique"):
        self.model = model
        self.field = field
        self.session = session
        self.message = message

    def __call__(self, form, field):
        query = self.session.query(self.model).filter(getattr(self.model, self.field) == field.data)

        # При редактировании — не считаем текущий объект за дубликат
        if hasattr(form, 'obj'):
            existing_value = getattr(form.obj, self.field, None)
            if existing_value == field.data:
                return

        if query.first():
            raise StopValidation(self.message)
