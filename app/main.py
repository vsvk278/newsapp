from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from app.database import engine, Base
from app.auth.routes import router as auth_router
from app.news.routes import router as news_router
from app.scheduler import start_scheduler


IMAGE_DIR = "static/article_images"
FALLBACK_IMAGE = "static/default-news.jpg"


# ---------- APP LIFESPAN ----------

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    yield


# ---------- APP SETUP ----------

app = FastAPI(lifespan=lifespan)

# Normal static files (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.include_router(auth_router)
app.include_router(news_router)


# ---------- SAFE IMAGE ROUTE (THIS FIXES EVERYTHING) ----------

@app.get("/article-image/{filename}")
def serve_article_image(filename: str):
    image_path = os.path.join(IMAGE_DIR, filename)

    if os.path.exists(image_path):
        return FileResponse(image_path)

    return FileResponse(FALLBACK_IMAGE)
