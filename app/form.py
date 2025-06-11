from admin.form import Form, PasswordField, \
    TextField, BooleanField, SelectField, TextareaField


class LoginForm(Form):
    text = TextField(label="text", required=True)
    password = PasswordField(label="password")
    textarea = TextareaField(label="textarea")
    checkbox = BooleanField(label='checkbox')
    switcher = BooleanField(label='switcher', template='/widgets/toggle.html')
    select = SelectField(label='select', items=[(1, 'Easy'), (2, 'Medium'), (3, 'Hard')])
    multiselect = SelectField(label='multiselect', items=[(1, 'Easy'), (2, 'Medium'), (3, 'Hard')], multi=True, template='/widgets/select.html')
    radio = SelectField(label='radio', items=[(1, 'Easy'), (2, 'Medium'), (3, 'Hard')], template='widgets/radio.html')