"""Create account, log in, log out, and "who am I" endpoints.

Security choices:
- Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes, the same recipe as
  the seed data, and checked by re-hashing and comparing in constant time (see passwords.py).
- After logging in, the browser gets a random session token in an HttpOnly
  cookie, which page scripts can't read. The database stores only a SHA-256
  hash of that token, so a leaked database can't be used to hijack a session.
- Failed logins get one generic message, take the same time whether or not the
  email exists, and are rate-limited per email and per IP address.
- Every query uses parameters, never string formatting, so SQL injection is blocked.
"""

from __future__ import annotations

import hashlib
import os
import re
import secrets
import sqlite3
import threading
import time
from collections import defaultdict, deque

from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel, SecretStr

from db import query, transaction
from passwords import dummy_hash, hash_password, password_problem, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])

SESSION_COOKIE = "cc_session"
SESSION_DAYS = 7
# Browsers only send Secure cookies over HTTPS; turn this on when the site is deployed.
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
MAX_EMAIL_LENGTH = 254
MAX_NAME_LENGTH = 50

GENERIC_LOGIN_ERROR = "That email and password don't match an account."


class AttemptLimiter:
    """Allows `limit` attempts per key within a rolling window, kept in memory."""

    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = limit
        self.window = window_seconds
        self._attempts: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def _prune(self, key: str, now: float) -> deque[float]:
        attempts = self._attempts[key]
        while attempts and attempts[0] <= now - self.window:
            attempts.popleft()
        return attempts

    def seconds_until_allowed(self, key: str) -> int:
        with self._lock:
            now = time.monotonic()
            attempts = self._prune(key, now)
            if len(attempts) < self.limit:
                return 0
            return int(attempts[0] + self.window - now) + 1

    def record(self, key: str) -> None:
        with self._lock:
            self._attempts[key].append(time.monotonic())

    def reset(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._attempts.clear()


failed_logins_by_email = AttemptLimiter(limit=5, window_seconds=15 * 60)
failed_logins_by_ip = AttemptLimiter(limit=20, window_seconds=15 * 60)
signups_by_ip = AttemptLimiter(limit=20, window_seconds=60 * 60)


class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: SecretStr  # SecretStr keeps passwords out of logs and error messages
    confirm_password: SecretStr


class LoginRequest(BaseModel):
    email: str
    password: SecretStr


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    member_since: str


def problem(status_code: int, message: str, field: str | None = None) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"message": message, "field": field})


def too_many_tries(wait_seconds: int) -> HTTPException:
    minutes = max(1, round(wait_seconds / 60))
    error = problem(
        status.HTTP_429_TOO_MANY_REQUESTS,
        f"Too many tries. Please wait about {minutes} minute{'s' if minutes != 1 else ''} and try again.",
    )
    error.headers = {"Retry-After": str(wait_seconds)}
    return error


def client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def normalize_email(email: str) -> str:
    return email.strip().lower()


def to_user(row: sqlite3.Row) -> User:
    first, last = row["first_name"], row["last_name"]
    if not first:  # older accounts only have the combined name
        first, _, last = row["name"].partition(" ")
    return User(
        id=row["id"],
        first_name=first,
        last_name=last or "",
        email=row["email"],
        member_since=row["created_at"],
    )


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def start_session(con: sqlite3.Connection, response: Response, user_id: int) -> None:
    token = secrets.token_urlsafe(32)
    con.execute(
        "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, datetime('now', ?))",
        (hash_token(token), user_id, f"+{SESSION_DAYS} days"),
    )
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=SESSION_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/api",
    )


def check_new_password(password: str, confirm: str, email: str) -> None:
    message = password_problem(password, email)
    if message:
        raise problem(400, message, "password")
    if confirm != password:
        raise problem(400, "Passwords need to match.", "confirm_password")


@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest, request: Request, response: Response) -> User:
    ip = client_ip(request)
    wait = signups_by_ip.seconds_until_allowed(ip)
    if wait:
        raise too_many_tries(wait)

    first_name = body.first_name.strip()
    last_name = body.last_name.strip()
    email = normalize_email(body.email)
    password = body.password.get_secret_value()

    if not first_name or len(first_name) > MAX_NAME_LENGTH:
        raise problem(400, "Enter your first name.", "first_name")
    if not last_name or len(last_name) > MAX_NAME_LENGTH:
        raise problem(400, "Enter your last name.", "last_name")
    if len(email) > MAX_EMAIL_LENGTH or not EMAIL_PATTERN.match(email):
        raise problem(400, "Enter a valid email address.", "email")
    check_new_password(password, body.confirm_password.get_secret_value(), email)

    # Hash before opening the transaction, so the slow step doesn't hold a write lock.
    password_hash = hash_password(password)
    signups_by_ip.record(ip)
    duplicate = problem(
        status.HTTP_409_CONFLICT, "An account with this email already exists. Try logging in instead.", "email"
    )
    with transaction() as con:
        if con.execute("SELECT 1 FROM users WHERE lower(email) = ?", (email,)).fetchone():
            raise duplicate
        try:
            cursor = con.execute(
                "INSERT INTO users (name, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
                (f"{first_name} {last_name}", email, password_hash, first_name, last_name),
            )
        except sqlite3.IntegrityError:  # someone signed up with this email a moment ago
            raise duplicate from None
        user_id = cursor.lastrowid
        start_session(con, response, user_id)
        row = con.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return to_user(row)


@router.post("/login", response_model=User)
def login(body: LoginRequest, request: Request, response: Response) -> User:
    email = normalize_email(body.email)
    ip = client_ip(request)
    wait = max(failed_logins_by_email.seconds_until_allowed(email), failed_logins_by_ip.seconds_until_allowed(ip))
    if wait:
        raise too_many_tries(wait)

    password = body.password.get_secret_value()
    with transaction() as con:
        row = con.execute("SELECT * FROM users WHERE lower(email) = ?", (email,)).fetchone()
        stored_hash = row["password_hash"] if row else dummy_hash()
        if not verify_password(stored_hash, password) or row is None:
            failed_logins_by_email.record(email)
            failed_logins_by_ip.record(ip)
            raise problem(status.HTTP_401_UNAUTHORIZED, GENERIC_LOGIN_ERROR)

        con.execute("DELETE FROM sessions WHERE expires_at <= datetime('now')")
        start_session(con, response, row["id"])

    failed_logins_by_email.reset(email)
    return to_user(row)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response) -> None:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        with transaction() as con:
            con.execute("DELETE FROM sessions WHERE token_hash = ?", (hash_token(token),))
    response.delete_cookie(SESSION_COOKIE, path="/api", httponly=True, secure=COOKIE_SECURE, samesite="lax")


def current_user(request: Request) -> User | None:
    """The shopper whose session cookie came with this request, or None."""
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        rows = query(
            """
            SELECT users.* FROM sessions JOIN users ON users.id = sessions.user_id
            WHERE sessions.token_hash = ? AND sessions.expires_at > datetime('now')
            """,
            (hash_token(token),),
        )
        if rows:
            return to_user(rows[0])
    return None


@router.get("/me", response_model=User | None)
def me(request: Request) -> User | None:
    """The logged-in shopper, or null for visitors (not an error, since most visitors aren't logged in)."""
    return current_user(request)
