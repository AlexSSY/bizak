from admin.form import Form, FormField, TextWidget


class LoginForm(Form):
    username = FormField(label="My father's name", type='text', widget=TextWidget(), required=True)
    password = FormField(label="My father's name", type='password', widget=TextWidget())
