"""Password storage: PBKDF2-HMAC-SHA256 with a random salt per password.

This matches the seed database exactly, so seeded accounts and new accounts
are checked the same way.

What's stored:  pbkdf2_sha256$<salt>$<hash>
- salt: random text made at signup (32 hex characters, from 16 random bytes)
- hash: PBKDF2-HMAC-SHA256 of the password, using that salt (as UTF-8 text) and
  120,000 iterations, written as 64 hex characters

A hash can't be reversed. To check a login, the typed password is hashed again
with the salt read out of the stored string, and the two hashes are compared in
constant time. Plain-text passwords are never stored, logged, or returned by the API.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from functools import cache

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 120_000  # must match the seed data; signup and login both use it
SALT_BYTES = 16

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

# A short list of the most-used passwords, which attackers always try first.
COMMON_PASSWORDS = {
    "password", "password1", "password123", "12345678", "123456789", "1234567890",
    "qwerty123", "qwertyuiop", "11111111", "00000000", "iloveyou", "sunshine",
    "princess", "football", "baseball", "welcome1", "letmein1", "abc12345",
    "trustno1", "bulldogs", "yaleyale", "boolaboola", "campuscustoms",
}


def password_problem(password: str, email: str) -> str | None:
    """Why a new password isn't allowed, or None if it's fine. Used by signup and set_password.py."""
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Use at least {MIN_PASSWORD_LENGTH} characters."
    if len(password) > MAX_PASSWORD_LENGTH:
        return f"Use {MAX_PASSWORD_LENGTH} characters or fewer."
    lowered = password.lower()
    if lowered in COMMON_PASSWORDS or lowered in {email.lower(), email.lower().partition("@")[0]}:
        return "That password is too easy to guess. Try a longer phrase."
    return None


def _digest(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), ITERATIONS).hex()


def hash_password(password: str, salt: str | None = None) -> str:
    """Signup: makes a new random salt (unless one is given, for tests) and returns the string to store."""
    salt = salt or secrets.token_hex(SALT_BYTES)
    return f"{ALGORITHM}${salt}${_digest(password, salt)}"


def verify_password(stored: str, password: str) -> bool:
    """Login: re-hashes the typed password with the stored salt and compares in constant time."""
    try:
        algorithm, salt, expected = stored.split("$")
    except ValueError:
        return False
    if algorithm != ALGORITHM or not salt:
        return False
    # compare_digest takes the same time wherever the strings differ, so response
    # times don't reveal how much of a guess was right.
    return hmac.compare_digest(_digest(password, salt), expected)


@cache
def dummy_hash() -> str:
    """A throwaway hash checked when an email isn't found, so a failed login takes
    the same time either way and doesn't reveal which emails have accounts."""
    return hash_password(secrets.token_hex(16))
