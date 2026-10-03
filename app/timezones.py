from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Used until an admin picks one on the admin page
DEFAULT_TIMEZONE = "America/Chicago"


def utc_now():
    """The current time as naive UTC -- the form every timestamp is stored in."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def is_valid_timezone(name: str):
    """True for an IANA name like "America/Denver"."""
    try:
        ZoneInfo(name)
        return True
    # ValueError covers malformed keys like "" or "../etc"
    except (ZoneInfoNotFoundError, ValueError):
        return False


def to_utc(dt: datetime, tz_name: str):
    """Converts an incoming time to naive UTC for storage.

    A naive time is what someone typed into a datetime-local input, so it's a
    wall-clock time in the site's timezone. A time with an offset (like the
    quick-extend buttons send) is already a fixed instant and only gets converted.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(tz_name))
    return dt.astimezone(timezone.utc).replace(tzinfo=None)
