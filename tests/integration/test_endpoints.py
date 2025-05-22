import re

import pytest

from login_app.app import create_app


@pytest.fixture()
def client(tmp_path):
    db = tmp_path / "test.db"
    app = create_app(db)
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def _set_csrf(client, token="test-token"):
    with client.session_transaction() as sess:
        sess["csrf_token"] = token
    return token


def test_register_login_logout_flow(client):
    token = _set_csrf(client)
    resp = client.post(
        "/register",
        data={
            "username": "alice",
            "email": "alice@example.com",
            "password": "Strong123",
            "csrf_token": token,
        },
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")

    token = _set_csrf(client)
    resp = client.post(
        "/login",
        data={
            "email": "alice@example.com",
            "password": "Strong123",
            "csrf_token": token,
        },
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/dashboard")

    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert re.search(b"alice", dashboard.data)

    token = _set_csrf(client)
    resp = client.post("/logout", data={"csrf_token": token}, follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")
    dash_resp = client.get("/dashboard")
    assert dash_resp.status_code == 302


def test_register_weak_password(client):
    token = _set_csrf(client)
    resp = client.post(
        "/register",
        data={
            "username": "bob",
            "email": "bob@example.com",
            "password": "weak",
            "csrf_token": token,
        },
    )
    assert resp.status_code == 200
    assert b"Password" in resp.data


def test_dashboard_requires_login(client):
    resp = client.get("/dashboard")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")
