from sqlalchemy.orm import Session
from app.model import User, UserAdmin
from admin.model import ModelAdmin


def test_model_admin_class(fake_db):
    instance = UserAdmin(User)
    assert instance != None

    view_context = instance.index_view(None, fake_db)
    columns = view_context.get('columns')
    assert columns
    assert columns[0] == 'ID'
    assert columns[1] == 'username'
    assert columns[2] == 'password'
    assert columns[3] == 'Custom'