from admin import site
from app.model import (
    Post, User, Flower, PostAdmin, UserAdmin, FlowerAdmin
)


def test_register_docs():
    docstring = site.register.__doc__
    assert docstring
    assert ':param model_class:' in docstring
    assert ':param model_admin_class:' in docstring


def test_register_successfully():
    site.register(User, UserAdmin)
    assert site.admin_model_storage.get(User).__class__ == UserAdmin