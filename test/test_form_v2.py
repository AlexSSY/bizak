from admin.form_v2 import Form
from admin.base_v2 import Field


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
