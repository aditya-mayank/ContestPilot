import pytest
import datetime
from contestpilot.utils import utc_now_iso

def test_utc_now_iso():
    # Should end with Z or +00:00
    iso = utc_now_iso()
    assert isinstance(iso, str)
    assert 'T' in iso
