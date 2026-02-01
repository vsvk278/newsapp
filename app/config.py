import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
DATABASE_URL = "sqlite:///./news_app.db"

# OpenAI API Configuration
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

RSS_FEEDS = {
    "Technology": "https://news.google.com/rss/search?q=technology&hl=en-US&gl=US&ceid=US:en",
    "Business": "https://news.google.com/rss/search?q=business&hl=en-US&gl=US&ceid=US:en",
    "Sports": "https://news.google.com/rss/search?q=sports&hl=en-US&gl=US&ceid=US:en",
    "Health": "https://news.google.com/rss/search?q=health&hl=en-US&gl=US&ceid=US:en"
}

FETCH_INTERVAL_HOURS = 12
