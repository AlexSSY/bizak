from admin.form import Form, FormField, TextWidget, form_field_validates


class LoginForm(Form):
    username = FormField(label="My father's name", type='text', widget=TextWidget(), required=True)
    password = FormField(label="My father's name", type='password', widget=TextWidget())

    @form_field_validates('username')
    def validate_username(self, value, session):
        return 'fake error'
