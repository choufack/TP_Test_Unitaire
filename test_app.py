import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_menu_add_and_get(client):
    # Ajout d'un nouvel article
    res = client.post("/menu", json={"name": "Tacos", "price": 4.0})
    assert res.status_code == 201

    # Récupération du menu
    res = client.get("/menu")
    assert res.status_code == 200
    data = res.get_json()
    assert any(item["name"] == "Tacos" for item in data)

def test_add_to_cart_and_order(client):
    # Ajout au panier
    res = client.post("/cart/add", json={"id": 1})
    assert res.status_code == 200

    # Création de commande
    res = client.post("/order")
    assert res.status_code == 201
    data = res.get_json()
    assert data["order"]["status"] == "Préparation"

def test_order_status_change(client):
    # Crée une commande
    client.post("/cart/add", json={"id": 1})
    res = client.post("/order")
    order_id = res.get_json()["order"]["id"]

    # Change le statut
    res = client.put(f"/order/{order_id}/status", json={"status": "Prête"})
    assert res.status_code == 200
    assert res.get_json()["order"]["status"] == "Prête"
