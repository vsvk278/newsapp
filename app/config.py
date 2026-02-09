import os

# =========================
# Core App Configuration
# =========================

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
DATABASE_URL = "sqlite:///./news_app.db"

FETCH_INTERVAL_HOURS = 12


# =========================
# INDIA-ONLY RSS FEEDS
# (High image reliability)
# =========================

RSS_FEEDS = {
    "Business": [
        # ✅ Excellent image embedding
        "https://www.livemint.com/rss/markets",
        "https://www.livemint.com/rss/companies",
        "https://www.moneycontrol.com/rss/latestnews.xml",

        # ⚠️ Mixed but better than others
        "https://www.thehindubusinessline.com/feeder/default.rss"
    ],

    "Technology": [
        # ✅ Best for tech images
        "https://www.livemint.com/rss/technology",

        # ✅ Startup / tech focus with proper media tags
        "https://yourstory.com/feed",
        "https://inc42.com/feed/"
    ],

    "Sports": [
        # ✅ Consistently provides images
        "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",

        # ⚠️ Sometimes missing but acceptable
        "https://www.icc-cricket.com/rss"
    ],

    "Health": [
        # ✅ Indian health coverage with images
        "https://www.livemint.com/rss/science",

        # ⚠️ Global but reliable media tags
        "https://medicalxpress.com/rss-feed/",
        "https://www.who.int/rss-feeds/news-english.xml"
    ]
}


# =========================
# Category Fallback Images
# (Used ONLY if article has no image)
# =========================

CATEGORY_FALLBACKS = {
    "Technology": "/static/fallback-technology.jpg",
    "Business": "/static/fallback-business.jpg",
    "Sports": "/static/fallback-sports.jpg",
    "Health": "/static/fallback-health.jpg"
}
