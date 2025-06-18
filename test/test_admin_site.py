import pytest

from admin import site
from app.model import (
    Post, User, Flower, PostAdmin, UserAdmin, FlowerAdmin
)


def test_register_successfully():
    site.register(User, UserAdmin)
    assert site.storage.get('user') == (User, UserAdmin)


@pytest.mark.parametrize("model_name", ["user", "User", "USER"])
def test_get_model_class(model_name):
    assert site.get_model_class(model_name) == User


@pytest.mark.parametrize("model_name", ["user", "User", "USER"])
def test_get_model_admin_instance(model_name):
    instance = site.get_model_admin_instance(model_name)
    assert instance.__class__ == UserAdmin


def test_get_all_sqlalchemy_models():
    assert User in site.get_all_sqlalchemy_models()
