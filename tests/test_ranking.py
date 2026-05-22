import pytest
from contestpilot.models import Contest
from contestpilot.ranking import rank_contest

def test_rank_contest():
    # Long duration (e.g. > 24 hours) -> LOW priority
    c1 = Contest(
        id="1", source_id="1", name="Long Challenge", platform="codechef",
        start_time="2026-06-01T10:00:00Z", end_time="2026-06-05T10:00:00Z",
        duration_seconds=345600, url="", status="UPCOMING"
    )
    priority, reason = rank_contest(c1)
    assert priority == "low"

    # Codeforces Div. 2 -> HIGH priority
    c2 = Contest(
        id="2", source_id="2", name="Codeforces Round 900 (Div. 2)", platform="codeforces",
        start_time="2026-06-01T18:00:00Z", end_time="2026-06-01T20:00:00Z",
        duration_seconds=7200, url="", status="UPCOMING"
    )
    priority, reason = rank_contest(c2)
    assert priority == "high"
    
    # Generic standard contest -> MEDIUM priority
    c3 = Contest(
        id="3", source_id="3", name="Weekly Match", platform="unknown_platform",
        start_time="2026-06-01T18:00:00Z", end_time="2026-06-01T20:00:00Z",
        duration_seconds=7200, url="", status="UPCOMING"
    )
    priority, reason = rank_contest(c3)
    assert priority == "medium"
