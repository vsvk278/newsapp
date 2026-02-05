import feedparser
import hashlib
import os
import re
import requests
from datetime import datetime
from urllib.parse import urljoin, urlparse
from io import BytesIO

from bs4 import BeautifulSoup
from PIL import Image
from sqlalchemy.orm import Session

from app.config import RSS_FEEDS
from app.models import Article


# ---------------- CONFIG ----------------

IMAGE_DIR = "static/article_images"

MIN_SIZE_BYTES = 15 * 1024
MIN_WIDTH = 400
MIN_HEIGHT = 250

# Indian publisher allow-list (critical)
ALLOWED_IMAGE_DOMAINS = [
    "indiatimes.com",
    "timesofindia.indiatimes.com",
    "thehindu.com",
    "ndtv.com",
    "indiatoday.in",
    "livemint.com",
    "moneycontrol.com",
    "news18.com",
    "hindustantimes.com",
]

os.makedirs(IMAGE_DIR, exist_ok=True)


# ---------------- UTILS ----------------

def strip_html(text: str) -> str:
    return re.sub(r"<.*?>", "", text or "").strip()


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def is_allowed_image_domain(url: str) -> bool:
    try:
        host = urlparse(url).hostname or ""
        return any(domain in host for domain in ALLOWED_IMAGE_DOMAINS)
    except Exception:
        return False


def download_image(url: str) -> str | None:
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None

        if not r.headers.get("Content-Type", "").startswith("image/"):
            return None

        if len(r.content) < MIN_SIZE_BYTES:
            return None

        img = Image.open(BytesIO(r.content))
        width, height = img.size

        if width < MIN_WIDTH or height < MIN_HEIGHT:
            return None

        ext = img.format.lower()
        filename = f"{hash_text(url)}.{ext}"
        path = os.path.join(IMAGE_DIR, filename)

        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(r.content)

        return f"/{path.replace(os.sep, '/')}"
    except Exception:
        return None


# ---------------- IMAGE EXTRACTION ----------------

def extract_rss_image(entry):
    if hasattr(entry, "media_content"):
        for m in entry.media_content:
            if "url" in m:
                return m["url"]

    if hasattr(entry, "media_thumbnail"):
        for m in entry.media_thumbnail:
            if "url" in m:
                return m["url"]

    if hasattr(entry, "links"):
        for link in entry.links:
            if link.get("type", "").startswith("image/"):
                return link.get("href")

    return None


def extract_publisher_image(article_url: str) -> str | None:
    try:
        r = requests.get(article_url, timeout=10)
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")

        # Prefer OG / Twitter images
        for prop in ["og:image", "twitter:image"]:
            tag = soup.find("meta", property=prop) or soup.find(
                "meta", attrs={"name": prop}
            )
            if tag and tag.get("content"):
                return urljoin(article_url, tag["content"])

        # Fallback to article body images
        for img in soup.select("article img, figure img, main img"):
            src = img.get("src")
            if src:
                return urljoin(article_url, src)

    except Exception:
        return None

    return None


# ---------------- FALLBACKS ----------------

def deterministic_stock_image(article_url: str) -> str:
    seed = hash_text(article_url)[:12]
    return f"https://picsum.photos/seed/{seed}/800/500"


def category_fallback(category: str) -> str:
    return {
        "Technology": "/static/fallback-technology.jpg",
        "Business": "/static/fallback-business.jpg",
        "Sports": "/static/fallback-sports.jpg",
        "Health": "/static/fallback-health.jpg",
    }.get(category, "/static/default-news.jpg")


# ---------------- RESOLVER ----------------

def resolve_article_image(entry, category: str) -> str:
    # 1️⃣ RSS image (only if Indian domain)
    url = extract_rss_image(entry)
    if url and is_allowed_image_domain(url):
        local = download_image(url)
        if local:
            return local

    # 2️⃣ Publisher page image (only if Indian domain)
    url = extract_publisher_image(entry.link)
    if url and is_allowed_image_domain(url):
        local = download_image(url)
        if local:
            return local

    # 3️⃣ Deterministic stock image (free, stable)
    stock_url = deterministic_stock_image(entry.link)
    local = download_image(stock_url)
    if local:
        return local

    # 4️⃣ Absolute local fallback
    return category_fallback(category)


# ---------------- MAIN PIPELINE ----------------

def fetch_and_store_news(db: Session):
    for category, feed_urls in RSS_FEEDS.items():
        for feed_url in feed_urls:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:10]:
                if not hasattr(entry, "title") or not hasattr(entry, "link"):
                    continue

                if db.query(Article).filter(Article.url == entry.link).first():
                    continue

                image_url = resolve_article_image(entry, category)

                published_at = datetime.utcnow()
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published_at = datetime(*entry.published_parsed[:6])

                article = Article(
                    title=strip_html(entry.title),
                    summary=strip_html(entry.get("summary", ""))[:500],
                    url=entry.link,
                    image_url=image_url,
                    category=category,
                    published_at=published_at,
                )

                db.add(article)

            db.commit()
