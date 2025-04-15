import os
import sys
print("Current working directory:", os.getcwd())
print("Python path:", sys.path)

sys.path.append('/Flask')
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_menu(client):
    response = client.get('/menu')
    assert response.status_code == 200
    assert len(response.json) > 0

def test_add_menu_item(client):
    new_item = {"id": 3, "name": "Pizza", "price": 8.0, "customizations": ["Extra Cheese"]}
    response = client.post('/menu', json=new_item)
    assert response.status_code == 201
    assert response.json["message"] == "Item added"

def test_create_order(client):
    order = {"items": [{"id": 1, "name": "Burger", "price": 5.0}]}
    response = client.post('/order', json=order)
