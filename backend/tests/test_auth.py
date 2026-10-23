"""Tests for creating accounts, logging in, and how passwords are stored.

The test database is a copy of data/campus_customs.db, so it includes the seeded
Test User (test@campuscustoms.yale.edu, password "password").

Run from backend/:  .venv/bin/python -m pytest
"""

import hashlib
import re
import sqlite3
import uuid

import passwords

PASSWORD = "correct horse battery staple"
SEED_EMAIL = "test@campuscustoms.yale.edu"
SEED_PASSWORD = "password"


def new_email() -> str:
    return f"shopper-{uuid.uuid4().hex[:10]}@example.com"


def signup(client, email, password=PASSWORD, **changes):
    body = {
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": email,
        "password": password,
        "confirm_password": password,
    }
    return client.post("/api/auth/signup", json=body | changes)


def stored_hash(db_path, email) -> str:
    with sqlite3.connect(db_path) as con:
        return con.execute("SELECT password_hash FROM users WHERE email = ?", (email,)).fetchone()[0]


def test_seeded_test_user_can_log_in(client):
    response = client.post("/api/auth/login", json={"email": SEED_EMAIL, "password": SEED_PASSWORD})
    assert response.status_code == 200
    assert response.json()["first_name"] == "Test"
    assert client.get("/api/auth/me").json()["email"] == SEED_EMAIL


def test_hash_recipe_matches_the_seed_format():
    expected = hashlib.pbkdf2_hmac("sha256", b"some password", b"abc123", 120_000).hex()
    assert passwords.hash_password("some password", salt="abc123") == f"pbkdf2_sha256$abc123${expected}"
    assert passwords.verify_password(f"pbkdf2_sha256$abc123${expected}", "some password")
    assert not passwords.verify_password(f"pbkdf2_sha256$abc123${expected}", "some passworD")
    for malformed in ["", "no-dollars", "md5$abc123$" + expected, "pbkdf2_sha256$$" + expected, "$argon2id$v=19$x$y"]:
        assert not passwords.verify_password(malformed, "some password")


def test_signup_saves_user_with_salted_pbkdf2_hash(client, db_path):
    email = new_email()
    response = signup(client, email)

    assert response.status_code == 201
    assert response.json() | {"id": 0, "member_since": ""} == {
        "id": 0,
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": email,
        "member_since": "",
    }
    password_hash = stored_hash(db_path, email)
    assert re.fullmatch(r"pbkdf2_sha256\$[0-9a-f]{32}\$[0-9a-f]{64}", password_hash)
    assert PASSWORD not in password_hash
    assert PASSWORD.encode() not in db_path.read_bytes()


def test_same_password_gets_a_different_hash_for_each_user(client, db_path):
    first, second = new_email(), new_email()
    signup(client, first)
    signup(client, second)
    assert stored_hash(db_path, first) != stored_hash(db_path, second)


def test_new_account_logs_in_with_the_same_hash_settings(client):
    email = new_email()
    signup(client, email)
    client.cookies.clear()
    response = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200


def test_session_cookie_is_http_only_and_only_its_hash_is_stored(client, db_path):
    response = signup(client, new_email())
    set_cookie = response.headers["set-cookie"]
    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie
    assert "Path=/api" in set_cookie

    token = response.cookies["cc_session"]
    with sqlite3.connect(db_path) as con:
        hashes = {row[0] for row in con.execute("SELECT token_hash FROM sessions")}
    assert token not in hashes
    assert hashlib.sha256(token.encode()).hexdigest() in hashes


def test_login_me_and_logout(client):
    email = new_email()
    signup(client, email)
    client.cookies.clear()
    assert client.get("/api/auth/me").json() is None

    response = client.post("/api/auth/login", json={"email": email.upper(), "password": PASSWORD})
    assert response.status_code == 200
    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert set(me.json()) == {"id", "first_name", "last_name", "email", "member_since"}

    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").json() is None


def test_wrong_password_and_unknown_email_get_the_same_answer(client):
    email = new_email()
    signup(client, email)
    client.cookies.clear()

    wrong_password = client.post("/api/auth/login", json={"email": email, "password": "not the password"})
    unknown_email = client.post("/api/auth/login", json={"email": new_email(), "password": PASSWORD})
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()
    assert "cc_session" not in wrong_password.cookies


def test_duplicate_email_is_rejected_regardless_of_case(client):
    email = new_email()
    assert signup(client, email).status_code == 201
    duplicate = signup(client, email.upper())
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"]["field"] == "email"


def test_signup_checks_every_field(client):
    cases = [
        ({"password": "short", "confirm_password": "short"}, "password"),
        ({"password": "password123", "confirm_password": "password123"}, "password"),
        ({"confirm_password": "something else"}, "confirm_password"),
        ({"email": "not-an-email"}, "email"),
        ({"first_name": "   "}, "first_name"),
        ({"last_name": ""}, "last_name"),
    ]
    for changes, field in cases:
        email = changes.pop("email", new_email())
        response = signup(client, email, **changes)
        assert response.status_code == 400, changes
        assert response.json()["detail"]["field"] == field


def test_repeated_failed_logins_are_blocked(client):
    email = new_email()
    signup(client, email)
    client.cookies.clear()
    for _ in range(5):
        assert client.post("/api/auth/login", json={"email": email, "password": "guess"}).status_code == 401

    blocked = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    assert blocked.status_code == 429
    assert "Retry-After" in blocked.headers


def test_injection_attempts_and_old_hash_formats_fail_safely(client):
    for email in ["' OR 1=1 --", "tauhid.zaman@yale.edu"]:
        response = client.post("/api/auth/login", json={"email": email, "password": "anything at all"})
        assert response.status_code == 401


def test_set_password_tool_gives_an_account_a_working_password(client, db_path):
    import set_password

    email = "tauhid.zaman@yale.edu"
    new_password = set_password.generate_password()
    assert passwords.password_problem(new_password, email) is None

    assert set_password.set_password(email, new_password) == "Tauhid Zaman"
    assert stored_hash(db_path, email).startswith("pbkdf2_sha256$")
    response = client.post("/api/auth/login", json={"email": email, "password": new_password})
    assert response.status_code == 200
    assert response.json()["first_name"] == "Tauhid"


def test_set_password_tool_refuses_weak_passwords_and_unknown_emails(client):
    import pytest
    import set_password

    with pytest.raises(ValueError):
        set_password.set_password("ada.1789818990@yale.edu", "password")
    with pytest.raises(LookupError):
        set_password.set_password(new_email(), set_password.generate_password())
