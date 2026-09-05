from apscheduler.schedulers.background import BackgroundScheduler

from .db import SessionLocal
from .refresh import refresh_watched


def _daily_refresh():
    session = SessionLocal()
    try:
        result = refresh_watched(session)
        print(f"[scheduler] daily refresh: {result}")
    finally:
        session.close()


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    # Weekday evenings after the US close. Data is end-of-day, so polling more
    # often would fetch nothing new. Hour is server-local; set for your timezone.
    scheduler.add_job(
        _daily_refresh, "cron", day_of_week="mon-fri", hour=22, minute=0,
        id="daily_refresh", replace_existing=True,
    )
    scheduler.start()
    return scheduler
