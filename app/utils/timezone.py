from datetime import datetime, timezone
from typing import Optional

def get_utc_now() -> datetime:
    """Get current UTC datetime with timezone info"""
    return datetime.now(timezone.utc)

def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Ensure datetime is UTC timezone aware"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def to_local_timezone(dt: Optional[datetime], target_tz: timezone = None) -> Optional[datetime]:
    """Convert UTC datetime to local timezone"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    if target_tz:
        return dt.astimezone(target_tz)
    return dt