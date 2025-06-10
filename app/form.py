from admin.form import Form, validates, PasswordField, \
    TextField, BooleanField, TextareaWidget


class LoginForm(Form):
    username = TextField(label="Username", required=True)
    password = PasswordField(label="Password")
    body = TextField(
        label="Body",
        widget=TextareaWidget(),
        validators=[
            lambda f, v, s: None if v else 'This field can not be empty',
            lambda f, v, s: 'Text can not contains "a" letters' if 'a' in v else None
        ]
    )
    remember = BooleanField(label='Remember Me')

    @validates('username', 'password')
    def validate_username(self, value, session):
        if len(value) < 3:
            return 'too short'
