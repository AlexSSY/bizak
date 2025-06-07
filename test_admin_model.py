from db import Session
from main import AdminModel, User


class AdminUser(AdminModel):
    pass


def test_instantiate_admin_user(fake_db):
    instance = AdminUser(User)
    assert instance != None
