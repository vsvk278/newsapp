from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.news.rss import fetch_and_store_news
from app.config import FETCH_INTERVAL_HOURS

scheduler = BackgroundScheduler()

def scheduled_fetch():
    db = SessionLocal()
    try:
        fetch_and_store_news(db)
    finally:
        db.close()

def start_scheduler():
    # Fetch news immediately on startup
    scheduled_fetch()
    
    # Schedule periodic fetches
    scheduler.add_job(
        scheduled_fetch,
        'interval',
        hours=FETCH_INTERVAL_HOURS,
        id='fetch_news',
        replace_existing=True
    )
    
    scheduler.start()
