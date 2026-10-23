"""Set a new password for a shopper account, stored the same way as at signup.

Nobody can look up an existing password, because only a salted one-way hash is
saved (see passwords.py). This tool replaces it with a new one instead.

Run from backend/:
    .venv/bin/python set_password.py EMAIL             # type a new password (hidden as you type)
    .venv/bin/python set_password.py EMAIL --generate  # make a strong random password and show it once

Setting a password also logs that account out everywhere.
"""

from __future__ import annotations

import argparse
import getpass
import secrets
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")  # hw4/.env

from db import ensure_schema, transaction  # noqa: E402
from passwords import hash_password, password_problem  # noqa: E402

# No look-alike characters (0/O, 1/l/I), so a generated password is easy to type.
ALPHABET = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
GROUPS, GROUP_SIZE = 4, 5  # 20 random characters, about 115 bits


def generate_password() -> str:
    return "-".join(
        "".join(secrets.choice(ALPHABET) for _ in range(GROUP_SIZE)) for _ in range(GROUPS)
    )


def ask_for_password(email: str) -> str:
    for _ in range(3):
        password = getpass.getpass(f"New password for {email}: ")
        problem = password_problem(password, email)
        if problem:
            print(f"  {problem}")
        elif getpass.getpass("Type it again: ") != password:
            print("  Those didn't match.")
        else:
            return password
    sys.exit("No password was set.")


def set_password(email: str, password: str) -> str:
    """Saves a new password hash, ends the account's sessions, and returns the account's name."""
    problem = password_problem(password, email)
    if problem:
        raise ValueError(problem)
    password_hash = hash_password(password)
    with transaction() as con:
        row = con.execute("SELECT id, name FROM users WHERE lower(email) = ?", (email.lower(),)).fetchone()
        if row is None:
            raise LookupError(f"No account uses {email}.")
        con.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, row["id"]))
        con.execute("DELETE FROM sessions WHERE user_id = ?", (row["id"],))
    return row["name"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Set a new password for a Campus Customs account.")
    parser.add_argument("email", help="the account's email address")
    parser.add_argument("--generate", action="store_true", help="create a strong random password and show it once")
    args = parser.parse_args()

    ensure_schema()
    password = generate_password() if args.generate else ask_for_password(args.email)
    try:
        name = set_password(args.email, password)
    except (LookupError, ValueError) as error:
        sys.exit(str(error))
    print(f"Password set for {name} <{args.email}>.")
    if args.generate:
        print(f"  New password: {password}")
        print("This password is shown only this once and can't be looked up later. Save it in a password manager.")


if __name__ == "__main__":
    main()
