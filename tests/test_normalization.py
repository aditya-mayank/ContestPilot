import pytest
from contestpilot.models import Contest

def test_contest_normalization():
    # Valid contest
    c = Contest(
        id="leetcode_123",
        source_id="123",
        name="Weekly Contest 400",
        platform="leetcode",
        start_time="2026-06-01T10:00:00Z",
        end_time="2026-06-01T11:30:00Z",
        duration_seconds=5400,
        url="https://leetcode.com/contest/weekly-contest-400",
        status="UPCOMING"
    )
    assert c.platform == "leetcode"
    assert c.duration_seconds == 5400
    assert c.status == "UPCOMING"
