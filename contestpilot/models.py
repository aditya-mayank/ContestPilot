from dataclasses import dataclass
from typing import Optional

@dataclass
class Contest:
    id: str
    source_id: str
    name: str
    platform: str
    start_time: str # ISO8601 UTC
    end_time: str # ISO8601 UTC
    duration_seconds: int
    url: str
    status: str
    calendar_event_id: Optional[str] = None

@dataclass
class UserPreference:
    key: str
    value: str

@dataclass
class SyncState:
    key: str
    value: str

@dataclass
class ReminderHistory:
    contest_id: str
    reminder_type: str
    sent_at: str # ISO8601 UTC

@dataclass
class ContestRanking:
    contest_id: str
    priority: str
    reason: str
