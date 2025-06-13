from admin.form import Form, PasswordField, \
    TextField, BooleanField, SelectField, TextareaField


class LoginForm(Form):
    text = TextField(label="text", required=True)
    password = PasswordField(label="password")
    textarea = TextareaField(label="textarea")
    checkbox = BooleanField(label='checkbox')
    switcher = BooleanField(label='switcher',
                            input_template='/widgets/toggle.html')
    select = SelectField(label='select',
                         items=[(1, 'Easy'), (2, 'Medium'), (3, 'Hard')])
    multiselect = SelectField(label='multiselect',
                              items=[(1, 'Easy'), (2, 'Medium'), (3, 'Hard')],
                              multi=True, input_template='/widgets/select.html')
    radio = SelectField(label='radio', items=[(1, 'Easy'), (2, 'Medium'), (3, 'Hard')],
                        input_template='widgets/radio.html')


fieldsets = (
    ("Main Info", { 'fields': ("user", "website") }),
    ("Phones", {
        'fields': (
            ("Primary", {'fields': (("primary_phone_country", "primary_phone_area", "primary_phone_number"),)}),
            ("Secondary", {'fields': (("secondary_phone_country", "secondary_phone_area", "secondary_phone_number"),)}),
        )
    })
)