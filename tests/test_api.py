import pytest
from app import create_app, db
from app.models.models import User, Product

#test
@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


def register_and_login(client, email="test@test.com", password="pass123", name="Test", role="customer"):
    client.post("/api/auth/register", json={"email": email, "password": password, "name": name})
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    return r.get_json()["access_token"]


def test_register(client):
    r = client.post("/api/auth/register", json={"email": "a@b.com", "password": "pw", "name": "A"})
    assert r.status_code == 201


def test_login_invalid(client):
    r = client.post("/api/auth/login", json={"email": "x@x.com", "password": "wrong"})
    assert r.status_code == 401


def test_product_list(client):
    r = client.get("/api/products/")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)


def test_add_to_cart_and_order(client):
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    # seed a product directly
    from app import db
    from app.models.models import Product
    with client.application.app_context():
        p = Product(name="Widget", price=9.99, stock=10)
        db.session.add(p)
        db.session.commit()
        pid = p.id

    r = client.post("/api/cart/", json={"product_id": pid, "quantity": 2}, headers=headers)
    assert r.status_code == 201

    r = client.post("/api/orders/", json={"shipping_address": "123 Main St"}, headers=headers)
    assert r.status_code == 201
    assert r.get_json()["total"] == 19.98
