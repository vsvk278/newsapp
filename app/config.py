import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
DATABASE_URL = "sqlite:///./news_app.db"

RSS_FEEDS = {
    "Business": [
        "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
        "https://www.moneycontrol.com/rss/latestnews.xml",
        "https://www.livemint.com/rss/markets"
    ],
    "Technology": [
        "https://www.thehindu.com/sci-tech/technology/feeder/default.rss",
        "https://www.indiatoday.in/rss/technology"
    ],
    "Sports": [
        "https://sports.ndtv.com/rss/all",
        "https://www.espncricinfo.com/rss/content/story/feeds/0.xml"
    ],
    "Health": [
        "https://www.thehindu.com/sci-tech/health/feeder/default.rss",
        "https://www.indiatoday.in/rss/health"
    ]
}


FETCH_INTERVAL_HOURS = 12

# Category fallback images
CATEGORY_FALLBACKS = {
    "Technology": "/static/fallback-technology.jpg",
    "Business": "/static/fallback-business.jpg",
    "Sports": "/static/fallback-sports.jpg",
    "Health": "/static/fallback-health.jpg"
}
