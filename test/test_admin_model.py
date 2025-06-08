from .conftest import Flower, FlowerAdmin


def test_model_admin_class(fake_db):
    instance = FlowerAdmin(Flower)
    assert instance != None

    view_context = instance.index_view(None, fake_db)
    columns = view_context.get('columns')
    assert columns != None
    assert columns[0] == 'id'
    assert columns[1] == 'name'
    assert columns[2] == 'color'
    assert columns[3] == 'created_at'
    assert columns[4] == 'updated_at'
    # records = view_context.get('records')
    # assert records != None
    # assert len(records) == 8
    # assert len(records[0]) == 4

def test_search_by_username(fake_db):
    # instance = User
    ...