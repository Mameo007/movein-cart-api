from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session                  # db session type
from ..models import Setting
from ..database import get_db
from ..schemas import SettingsResponse
from ..timezones import DEFAULT_TIMEZONE

router = APIRouter()

TIMEZONE_KEY = "timezone"


def get_site_timezone(db):
    """The timezone due times are typed in and shown in, e.g. "America/Denver"."""
    setting = db.query(Setting).filter(Setting.key == TIMEZONE_KEY).first()
    return setting.value if setting else DEFAULT_TIMEZONE


def set_site_timezone(db, tz_name):
    setting = db.query(Setting).filter(Setting.key == TIMEZONE_KEY).first()
    if setting:
        setting.value = tz_name
    else:
        db.add(Setting(key=TIMEZONE_KEY, value=tz_name))


# Public -- the checkout form needs it to label the due time
@router.get("/api/settings", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    return SettingsResponse(timezone=get_site_timezone(db))
