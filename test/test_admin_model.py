from .conftest import Flower, FlowerAdmin
from app.server import app
from fastapi.testclient import TestClient


client = TestClient(app)


def test_model_admin_class(fake_db):
    flower_admin_instance = FlowerAdmin(Flower)

    # view_context = flower_admin_instance.index_view(None, fake_db)

    response = client.get('/Flower')

    assert response.status_code == 200

    # columns = view_context.get('columns')
    # assert columns != None
    # assert columns == ['id', 'name', 'color', 'created_at', 'updated_at']

    # records = view_context.get('records')
    # assert records != None
    # assert len(records) == 8
    # assert len(records[0]) == 5

def test_search(fake_db):
    flower_admin_instance = FlowerAdmin(Flower)
    