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

def create_cart(cart_number):
    # Carts can only be created by the admin now
    return client.post("/api/admin/carts", json={"cart_number": cart_number}, headers=admin_headers())

def test_get_carts():
    response = client.get("/api/carts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_public_cart_create_is_gone():
    response = client.post("/api/carts", json={"cart_number": "TEST123"})
    assert response.status_code == 405

def test_create_cart():
    response = create_cart("TEST123")
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
    cart_id = create_cart("CHECKOUT123").json()["id"]

    checkout_response = client.post(f"/api/carts/{cart_id}/checkout", json=CHECKOUT_BODY)
    assert checkout_response.status_code == 200
    data = checkout_response.json()
    assert data["cart_id"] == cart_id

def test_checkout_already_in_use():
    # Create and checkout a cart, then try to checkout again
    cart_id = create_cart("INUSE123").json()["id"]
    client.post(f"/api/carts/{cart_id}/checkout", json=CHECKOUT_BODY)

    response = client.post(f"/api/carts/{cart_id}/checkout", json=CHECKOUT_BODY)
    assert response.status_code == 400

def test_return_cart():
    # Create a cart, check it out, then return it
    cart_id = create_cart("RETURN123").json()["id"]
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
    cart_id = create_cart(cart_number).json()["id"]
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
    headers = admin_headers()
    client.put("/api/admin/settings/timezone", json={"timezone": "America/New_York"}, headers=headers)

    # Noon typed in Eastern (EDT, UTC-4) is stored and returned as 16:00 UTC
    response = client.patch(
        f"/api/admin/sessions/{session['id']}",
        json={"due_at": "2026-06-10T12:00:00"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["due_at"] == "2026-06-10T16:00:00Z"

def test_admin_update_due_at_with_offset_ignores_site_timezone():
    # The quick-extend buttons send an exact instant, so the site zone doesn't apply
    session = checked_out_session("ADMIN_OFFSET")
    response = client.patch(
        f"/api/admin/sessions/{session['id']}",
        json={"due_at": "2026-06-10T16:00:00Z"},
        headers=admin_headers(),
    )
    assert response.json()["due_at"] == "2026-06-10T16:00:00Z"

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

def test_admin_session_history():
    active = checked_out_session("HIST_ACTIVE")
    returned = checked_out_session("HIST_RETURNED")
    client.post(f"/api/carts/{returned['cart_id']}/return")
    headers = admin_headers()

    past = client.get("/api/admin/sessions?status=returned", headers=headers).json()
    assert [s["id"] for s in past] == [returned["id"]]
    assert past[0]["returned_at"] is not None

    everything = client.get("/api/admin/sessions?status=all", headers=headers).json()
    assert {s["id"] for s in everything} == {active["id"], returned["id"]}

def test_admin_session_history_rejects_unknown_status():
    response = client.get("/api/admin/sessions?status=bogus", headers=admin_headers())
    assert response.status_code == 422

def test_admin_force_return():
    session = checked_out_session("FORCE_RETURN")

    response = client.post(f"/api/admin/sessions/{session['id']}/return", headers=admin_headers())
    assert response.status_code == 200
    assert response.json()["returned_at"] is not None

    cart = next(c for c in client.get("/api/carts").json() if c["id"] == session["cart_id"])
    assert cart["status"] == "AVAILABLE"

def test_admin_force_return_twice():
    session = checked_out_session("FORCE_TWICE")
    headers = admin_headers()
    client.post(f"/api/admin/sessions/{session['id']}/return", headers=headers)

    response = client.post(f"/api/admin/sessions/{session['id']}/return", headers=headers)
    assert response.status_code == 400

def test_admin_force_return_requires_token():
    response = client.post("/api/admin/sessions/1/return")
    assert response.status_code == 401

def test_admin_create_cart_requires_token():
    response = client.post("/api/admin/carts", json={"cart_number": "NOPE"})
    assert response.status_code == 401

def test_admin_create_duplicate_cart():
    create_cart("DUPE")
    response = create_cart("DUPE")
    assert response.status_code == 400

def test_maintenance_cart_cannot_be_checked_out():
    cart_id = create_cart("MAINT").json()["id"]
    headers = admin_headers()

    response = client.patch(f"/api/admin/carts/{cart_id}", json={"status": "MAINTENANCE"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "MAINTENANCE"

    assert client.post(f"/api/carts/{cart_id}/checkout", json=CHECKOUT_BODY).status_code == 400
    assert client.post(f"/api/carts/{cart_id}/return").status_code == 400

    response = client.patch(f"/api/admin/carts/{cart_id}", json={"status": "AVAILABLE"}, headers=headers)
    assert response.json()["status"] == "AVAILABLE"

def test_admin_cannot_set_in_use():
    cart_id = create_cart("NO_IN_USE").json()["id"]
    response = client.patch(f"/api/admin/carts/{cart_id}", json={"status": "IN_USE"}, headers=admin_headers())
    assert response.status_code == 422

def test_admin_cannot_change_status_of_checked_out_cart():
    session = checked_out_session("BUSY_STATUS")
    response = client.patch(
        f"/api/admin/carts/{session['cart_id']}", json={"status": "MAINTENANCE"}, headers=admin_headers()
    )
    assert response.status_code == 400

def test_admin_delete_cart_with_history():
    session = checked_out_session("DELETE_ME")
    client.post(f"/api/carts/{session['cart_id']}/return")
    headers = admin_headers()

    response = client.delete(f"/api/admin/carts/{session['cart_id']}", headers=headers)
    assert response.status_code == 204
    assert session["cart_id"] not in [c["id"] for c in client.get("/api/carts").json()]
    assert client.get("/api/admin/sessions?status=all", headers=headers).json() == []

def test_admin_cannot_delete_checked_out_cart():
    session = checked_out_session("BUSY_DELETE")
    response = client.delete(f"/api/admin/carts/{session['cart_id']}", headers=admin_headers())
    assert response.status_code == 400

def test_admin_delete_nonexistent_cart():
    response = client.delete("/api/admin/carts/9999", headers=admin_headers())
    assert response.status_code == 404

# --- TIMEZONE ---

def test_default_timezone():
    response = client.get("/api/settings")
    assert response.status_code == 200
    assert response.json() == {"timezone": "America/Chicago"}

def test_checkout_due_at_uses_site_timezone():
    client.put("/api/admin/settings/timezone", json={"timezone": "America/Denver"}, headers=admin_headers())

    # 18:00 Mountain (MDT, UTC-6) is midnight UTC the next day
    session = checked_out_session("TZ_CHECKOUT")
    assert session["due_at"] == "2026-06-08T00:00:00Z"

def test_timestamps_are_marked_utc():
    session = checked_out_session("TZ_STAMPS")
    assert session["checked_out_at"].endswith("Z")

    returned = client.post(f"/api/admin/sessions/{session['id']}/return", headers=admin_headers()).json()
    assert returned["returned_at"].endswith("Z")

def test_update_timezone():
    headers = admin_headers()
    response = client.put("/api/admin/settings/timezone", json={"timezone": "Pacific/Honolulu"}, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"timezone": "Pacific/Honolulu"}

    # Saving twice updates the one row rather than adding another
    client.put("/api/admin/settings/timezone", json={"timezone": "America/Phoenix"}, headers=headers)
    assert client.get("/api/settings").json() == {"timezone": "America/Phoenix"}

def test_update_timezone_rejects_unknown():
    for bad in ["Mars/Olympus_Mons", "", "../etc/passwd"]:
        response = client.put("/api/admin/settings/timezone", json={"timezone": bad}, headers=admin_headers())
        assert response.status_code == 422

def test_update_timezone_requires_token():
    response = client.put("/api/admin/settings/timezone", json={"timezone": "America/Denver"})
    assert response.status_code == 401
