import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

client = TestClient(app)

def test_get_carts():
    response = client.get("/api/carts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_cart():
    response = client.post("/api/carts", json={"cart_number": "TEST123"})
    assert response.status_code == 200
    data = response.json()
    assert data["cart_number"] == "TEST123"
    assert data["status"] == "AVAILABLE"

CHECKOUT_BODY = {
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "1234567890",
    "room_number": "101",
    "due_at": "2026-06-07T18:00:00"
}

def test_checkout_cart():
    # Create a cart, then check it out
    cart_id = client.post("/api/carts", json={"cart_number": "CHECKOUT123"}).json()["id"]

    checkout_response = client.post(f"/api/carts/{cart_id}/checkout", json=CHECKOUT_BODY)
    assert checkout_response.status_code == 200
    data = checkout_response.json()
    assert data["cart_id"] == cart_id

def test_checkout_already_in_use():
    # Create and checkout a cart, then try to checkout again
    cart_id = client.post("/api/carts", json={"cart_number": "INUSE123"}).json()["id"]
    client.post(f"/api/carts/{cart_id}/checkout", json=CHECKOUT_BODY)

    response = client.post(f"/api/carts/{cart_id}/checkout", json=CHECKOUT_BODY)
    assert response.status_code == 400

def test_return_cart():
    # Create a cart, check it out, then return it
    cart_id = client.post("/api/carts", json={"cart_number": "RETURN123"}).json()["id"]
    client.post(f"/api/carts/{cart_id}/checkout", json=CHECKOUT_BODY)

    return_response = client.post(f"/api/carts/{cart_id}/return")
    assert return_response.status_code == 200
    data = return_response.json()
    assert data["status"] == "AVAILABLE"

def test_checkout_nonexistent_cart():
    response = client.post("/api/carts/9999/checkout", json=CHECKOUT_BODY)
    assert response.status_code == 404

def test_return_nonexistent_cart():
    response = client.post("/api/carts/9999/return")
    assert response.status_code == 404
