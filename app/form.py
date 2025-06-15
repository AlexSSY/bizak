from wtforms import Form, PasswordField, \
    BooleanField, SelectField, StringField
from wtforms.widgets import RadioInput


class LoginForm(Form):
    text = StringField(label="text", required=True)
    password = PasswordField(label="password")
    textarea = StringField(label="textarea")
    checkbox = BooleanField(label='checkbox')
    switcher = BooleanField(label='switcher',
                            input_template='/widgets/toggle.html')
    select = SelectField(label='select',
                         choices=[(1, 'Easy'), (2, 'Medium'), (3, 'Hard')],
                         coerce=int)
    multiselect = SelectField(label='multiselect',
                              choices=[(1, 'Easy'), (2, 'Medium'), (3, 'Hard')],
                              coerce=int)
    radio = SelectField(label='radio', choices=[(1, 'Easy'), (2, 'Medium'), (3, 'Hard')], widget=RadioInput())


fieldsets = (
    ("Main Info", { 'fields': ("user", "website") }),
    ("Phones", {
        'fields': (
            ("Primary", {'fields': (("primary_phone_country", "primary_phone_area", "primary_phone_number"),)}),
            ("Secondary", {'fields': (("secondary_phone_country", "secondary_phone_area", "secondary_phone_number"),)}),
        )
    })
)