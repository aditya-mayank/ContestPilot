import pytest
import os
from contestpilot.database import init_db

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    # Use a temp DB for all tests to prevent polluting production DB
    temp_db = "test_contestpilot_global.db"
    monkeypatch.setattr("contestpilot.database.DB_PATH", temp_db)
    init_db()
    yield
    if os.path.exists(temp_db):
        try:
            os.remove(temp_db)
        except PermissionError:
            pass
