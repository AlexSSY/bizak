from sqlalchemy.orm import Session
from app.model import User, UserAdmin
from admin.model import ModelAdmin
from conftest import Base


def test_model_admin_class(fake_db):
    instance = UserAdmin(User)
    assert instance != None

    view_context = instance.index_view(None, fake_db)
    columns = view_context.get('columns')
    assert columns != None
    assert columns[0] == 'ID'
    assert columns[1] == 'username'
    assert columns[2] == 'password'
    assert columns[3] == 'Custom'
    records = view_context.get('records')
    assert records != None
    assert len(records) == 8
    assert len(records[0]) == 4

def test_search_by_username(fake_db):
    instance = User