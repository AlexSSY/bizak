import pytest


def test_index(client):
    response = client.get('/admin/Flower')
    assert response.status_code == 200
    response_json = response.json()
    columns = response_json.get('columns')
    assert columns != None
    assert columns == ['id', 'name', 'color', 'created_at', 'updated_at']
    records = response_json.get('records')
    assert records != None
    assert len(records) == 8
    assert records[0][:3] == [1, 'Роза', 'красный']


def test_search(client):
    # flower_admin_instance = FlowerAdmin(Flower)
    response = client.get('admin/Flower', params={'search': 'Роза'})
    assert response.status_code == 200
    response_json = response.json()
    records = response_json.get('records')
    assert records != None
    assert len(records) == 1
    assert records[0][:3] == [1, 'Роза', 'красный']
    

def test_offset(client):
    response = client.get('admin/Flower', params={'offset': 11})
    assert response.status_code == 200
    response_json = response.json()
    records = response_json.get('records')
    assert records != None
    assert len(records) == 1
    assert records[0][:3] == [12, 'Чертополох', 'желтый']


def test_limit(client):
    response = client.get('admin/Flower', params={'limit': 3})
    assert response.status_code == 200
    response_json = response.json()
    records = response_json.get('records')
    assert records != None
    assert len(records) == 3
    assert records[-1][:3] == [3, 'Ласточкина трава', 'белый']


@pytest.mark.parametrize('limit', [-1, 0])
def test_limit_unreasonable_values_returns_default(client, limit):
    response = client.get('admin/Flower', params={'limit': limit})
    assert response.status_code == 200
    response_json = response.json()
    records = response_json.get('records')
    assert records != None
    assert len(records) == 1
    assert records[0][:3] == [1, 'Роза', 'красный']


def test_order_default(client):
    response = client.get('admin/Flower', params={'order': 'id'})
    assert response.status_code == 200
    response_json = response.json()
    records = response_json.get('records')
    assert records != None
    assert len(records) == 8
    assert records[-1][:3] == [8, 'Себачая петрушка', 'белый']


def test_order_asc(client):
    response = client.get('admin/Flower', params={'order': 'id', 'order_type': 'asc'})
    assert response.status_code == 200
    response_json = response.json()
    records = response_json.get('records')
    assert records != None
    assert len(records) == 8
    assert records[-1][:3] == [8, 'Себачая петрушка', 'белый']


def test_order_desc(client):
    response = client.get('admin/Flower', params={'order': 'id', 'order_type': 'desc'})
    assert response.status_code == 200
    response_json = response.json()
    records = response_json.get('records')
    assert records != None
    assert len(records) == 8
    assert records[-1][:3] == [5, 'Сирень', 'синий']


def test_flower_filter_by_name(client):
    response = client.get('admin/Flower', params={'filters[name]': 'Роза'})
    assert response.status_code == 200
    response_json = response.json()
    records = response_json.get('records')
    assert len(records) == 1
    assert records[0][:3] == [1, 'Роза', 'красный']


def test_flower_filter_by_id_gte(client):
    response = client.get('admin/Flower', params={'filters[id__gte]': 3})
    assert response.status_code == 200
    response_json = response.json()
    records = response_json.get('records')
    assert len(records) == 8
    assert records[0][:3] == [3, 'Ласточкина трава', 'белый']
    assert records[-1][:3] == [10, 'Омела', 'белый']


def test_flower_filter_by_id_gt(client):
    response = client.get('admin/Flower', params={'filters[id__gt]': 3})
    assert response.status_code == 200
    response_json = response.json()
    records = response_json.get('records')
    assert len(records) == 8
    assert records[0][0] == 4
    assert records[-1][0] == 11


def test_flower_filter_by_id_lt(client):
    response = client.get('admin/Flower', params={'filters[id__lt]': 3})
    assert response.status_code == 200
    response_json = response.json()
    records = response_json.get('records')
    assert len(records) == 2
    assert records[0][0] == 1
    assert records[-1][0] == 2


def test_flower_filter_by_id_lte(client):
    response = client.get('admin/Flower', params={'filters[id__lte]': 3})
    assert response.status_code == 200
    response_json = response.json()
    records = response_json.get('records')
    assert len(records) == 3
    assert records[0][0] == 1
    assert records[-1][0] == 3


def test_flower_filter_by_id_ne(client):
    response = client.get('admin/Flower', params={'filters[id__ne]': 3})
    assert response.status_code == 200
    response_json = response.json()
    records = response_json.get('records')
    assert len(records) == 8
    records_ids = list([r[0] for r in records])
    assert 3 not in records_ids


def test_flower_filter_by_id_eq(client):
    response = client.get('admin/Flower', params={'filters[id__eq]': 3})
    assert response.status_code == 200
    response_json = response.json()
    records = response_json.get('records')
    assert len(records) == 1
    assert records[0][0] == 3
