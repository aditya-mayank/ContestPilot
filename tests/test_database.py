import pytest
import os
import sqlite3
import datetime
from contestpilot.database import DB_PATH, init_db, save_contest, get_connection
from contestpilot.models import Contest

def test_duplicate_prevention_upsert():
    c = Contest(
        id="test_1", source_id="1", name="Test Contest", platform="leetcode",
        start_time="2026-06-01T10:00:00Z", end_time="2026-06-01T12:00:00Z",
        duration_seconds=7200, url="", status="UPCOMING"
    )
    
    # Save once
    save_contest(c)
    
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM contests WHERE id='test_1'").fetchone()[0]
    assert count == 1
    
    # Save again (should upsert, not duplicate)
    c.name = "Test Contest Updated"
    save_contest(c)
    
    count = conn.execute("SELECT COUNT(*) FROM contests WHERE id='test_1'").fetchone()[0]
    assert count == 1
    
    name = conn.execute("SELECT name FROM contests WHERE id='test_1'").fetchone()[0]
    assert name == "Test Contest Updated"
    conn.close()
