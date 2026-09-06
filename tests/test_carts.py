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

# --- ADMIN ---

ADMIN_PASSWORD = "test-admin-password"

@pytest.fixture(autouse=True)
def admin_env(monkeypatch):
    monkeypatch.setenv("ADMIN_PASSWORD", ADMIN_PASSWORD)
    # HS256 wants at least 32 bytes of key
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-secret-that-is-long-enough-for-hs256")

def admin_headers():
    token = client.post("/api/admin/login", json={"password": ADMIN_PASSWORD}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def checked_out_session(cart_number):
    # Create a cart and check it out, returning the new session
    cart_id = client.post("/api/carts", json={"cart_number": cart_number}).json()["id"]
    return client.post(f"/api/carts/{cart_id}/checkout", json=CHECKOUT_BODY).json()

def test_admin_login_wrong_password():
    response = client.post("/api/admin/login", json={"password": "wrong"})
    assert response.status_code == 401

def test_admin_login_success():
    response = client.post("/api/admin/login", json={"password": ADMIN_PASSWORD})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"

def test_admin_sessions_requires_token():
    response = client.get("/api/admin/sessions")
    assert response.status_code == 401

def test_admin_sessions_rejects_bad_token():
    response = client.get("/api/admin/sessions", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401

def test_admin_update_due_at_requires_token():
    response = client.patch("/api/admin/sessions/1", json={"due_at": "2026-06-08T18:00:00"})
    assert response.status_code == 401

def test_admin_lists_only_active_sessions():
    active = checked_out_session("ADMIN_ACTIVE")
    returned = checked_out_session("ADMIN_RETURNED")
    client.post(f"/api/carts/{returned['cart_id']}/return")

    response = client.get("/api/admin/sessions", headers=admin_headers())
    assert response.status_code == 200

    listed = response.json()
    assert [s["id"] for s in listed] == [active["id"]]
    assert listed[0]["cart_number"] == "ADMIN_ACTIVE"

def test_admin_sessions_sorted_by_due_at():
    later = checked_out_session("ADMIN_LATER")
    sooner = checked_out_session("ADMIN_SOONER")

    headers = admin_headers()
    client.patch(f"/api/admin/sessions/{later['id']}", json={"due_at": "2026-06-09T18:00:00"}, headers=headers)
    client.patch(f"/api/admin/sessions/{sooner['id']}", json={"due_at": "2026-06-07T18:00:00"}, headers=headers)

    listed = client.get("/api/admin/sessions", headers=headers).json()
    assert [s["id"] for s in listed] == [sooner["id"], later["id"]]

def test_admin_update_due_at():
    session = checked_out_session("ADMIN_UPDATE")

    response = client.patch(
        f"/api/admin/sessions/{session['id']}",
        json={"due_at": "2026-06-10T12:00:00"},
        headers=admin_headers(),
    )
    assert response.status_code == 200
    assert response.json()["due_at"] == "2026-06-10T12:00:00"

def test_admin_update_due_at_nonexistent_session():
    response = client.patch("/api/admin/sessions/9999", json={"due_at": "2026-06-10T12:00:00"}, headers=admin_headers())
    assert response.status_code == 404

def test_admin_update_due_at_returned_session():
    session = checked_out_session("ADMIN_DONE")
    client.post(f"/api/carts/{session['cart_id']}/return")

    response = client.patch(
        f"/api/admin/sessions/{session['id']}",
        json={"due_at": "2026-06-10T12:00:00"},
        headers=admin_headers(),
    )
    assert response.status_code == 400
