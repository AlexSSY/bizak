from admin.forms_v2 import Form
from admin.fields_v2 import Field
from admin.widgets_v2 import Widget


def test_form_can_collect_declared_fields():
    class TestForm(Form):
        field1 = Field('field1')
        field2 = Field('field1')

    assert TestForm.declared_fields.get('field1')
    assert TestForm.declared_fields.get('field2')
    assert not getattr(TestForm, 'field1', None)
    assert not getattr(TestForm, 'field2', None)


def test_form_can_collect_declared_fields_from_subclass():
    class TestForm1(Form):
        field1 = Field('field1')

    class TestForm2(TestForm1):
        field1 = Field('field2')

    assert len(TestForm2.declared_fields) == 1
    field = TestForm2.declared_fields.get('field1') 
    assert field
    assert field.name == 'field2'


def test_form_can_assign_declared_field_name_from_attribute():
    class TestForm(Form):
        username = Field()
        password = Field(name='')

    assert TestForm.declared_fields
    assert TestForm.declared_fields['username'].name == 'username'
    assert TestForm.declared_fields['password'].name == 'password'


import os
from fastapi.templating import Jinja2Templates
CURRENT_PATH = os.path.dirname(__file__)
templating = Jinja2Templates(os.path.join(CURRENT_PATH, 'templates/test/'))


def test_widget_renderable():
    widget = Widget('widget.html')
    assert hasattr(widget, 'render')


def test_widget_renders_template():
    widget = Widget('/widget.html')
    html = widget.render(templating)
    assert html == '<p>test</p>'


def test_widgtet_renders_template_with_context():
    widget = Widget('/widget_ctx.html')
    html = widget.render(templating)
    assert html == '<p>test</p>'
