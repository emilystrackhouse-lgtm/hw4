"""Test setup: every test run works on a throwaway copy of the database.

The copy is made and CAMPUS_CUSTOMS_DB is pointed at it here, at import time,
before pytest imports any test file. Backend modules read the database path
when they're first imported, so doing this any later would let tests write to
the real database.
"""

import atexit
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parent.parent
SOURCE_DB = BACKEND_DIR.parent / "data" / "campus_customs.db"

_test_dir = Path(tempfile.mkdtemp(prefix="campus-customs-tests-"))
atexit.register(shutil.rmtree, _test_dir, ignore_errors=True)
TEST_DB = _test_dir / "campus_customs.db"
shutil.copy(SOURCE_DB, TEST_DB)
os.environ["CAMPUS_CUSTOMS_DB"] = str(TEST_DB)
TEST_AUDIT_LOG = _test_dir / "audit_trail.json"
os.environ["CAMPUS_CUSTOMS_AUDIT_LOG"] = str(TEST_AUDIT_LOG)  # tests never touch output/audit_trail.json
sys.path.insert(0, str(BACKEND_DIR))

import db  # noqa: E402

# Stop right away if anything ever points the tests at the real database.
assert db.DB_PATH.resolve() == TEST_DB.resolve(), f"Tests must not use {db.DB_PATH}"

import audit  # noqa: E402

assert audit.AUDIT_PATH.resolve() == TEST_AUDIT_LOG.resolve(), f"Tests must not use {audit.AUDIT_PATH}"


@pytest.fixture(scope="session")
def app():
    import main

    return main.app


@pytest.fixture
def client(app):
    import auth
    import main

    for limiter in (
        auth.failed_logins_by_email,
        auth.failed_logins_by_ip,
        auth.signups_by_ip,
        main.chat_messages_by_ip,
    ):
        limiter.clear()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_path():
    return TEST_DB


@pytest.fixture
def audit_log():
    return TEST_AUDIT_LOG
