from admin.form import Form, validates, PasswordField, \
    TextField, BooleanField, TextareaWidget, SelectField, SelectWidget, \
    ToggleWidget


class LoginForm(Form):
    text = TextField(label="text", required=True)
    password = PasswordField(label="password")
    textarea = TextField(label="textarea", widget=TextareaWidget())
    checkbox = BooleanField(label='checkbox')
    switcher = BooleanField(label='switcher', widget=ToggleWidget())
    select = SelectField(label='select', items=[(1, 'Easy'), (2, 'Medium'), (3, 'Hard')])
    multiselect = SelectField(label='multiselect', items=[(1, 'Easy'), (2, 'Medium'), (3, 'Hard')], widget=SelectWidget(multi=True))
    radio = SelectField(label='radio', items=[(1, 'Easy'), (2, 'Medium'), (3, 'Hard')], widget=SelectWidget(template_name='widgets/radio.html'))