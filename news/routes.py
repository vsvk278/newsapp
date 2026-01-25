from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Article, Bookmark
from app.auth.routes import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login")
    
    articles = db.query(Article).order_by(Article.published_at.desc()).limit(40).all()
    
    bookmarked_ids = set()
    if current_user:
        bookmarks = db.query(Bookmark).filter(Bookmark.user_id == current_user.id).all()
        bookmarked_ids = {b.article_id for b in bookmarks}
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "articles": articles,
        "current_user": current_user,
        "bookmarked_ids": bookmarked_ids,
        "category": "Latest"
    })

@router.get("/category/{category_name}", response_class=HTMLResponse)
async def category(request: Request, category_name: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login")
    
    articles = db.query(Article).filter(Article.category == category_name).order_by(Article.published_at.desc()).limit(40).all()
    
    bookmarked_ids = set()
    if current_user:
        bookmarks = db.query(Bookmark).filter(Bookmark.user_id == current_user.id).all()
        bookmarked_ids = {b.article_id for b in bookmarks}
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "articles": articles,
        "current_user": current_user,
        "bookmarked_ids": bookmarked_ids,
        "category": category_name
    })

@router.post("/bookmark/{article_id}")
async def bookmark(article_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login")
    
    existing = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.article_id == article_id
    ).first()
    
    if existing:
        db.delete(existing)
    else:
        bookmark = Bookmark(user_id=current_user.id, article_id=article_id)
        db.add(bookmark)
    
    db.commit()
    return RedirectResponse(url=request.headers.get("referer", "/"), status_code=303)

@router.get("/bookmarks", response_class=HTMLResponse)
async def bookmarks(request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login")
    
    bookmarks = db.query(Bookmark).filter(Bookmark.user_id == current_user.id).all()
    articles = [b.article for b in bookmarks]
    
    bookmarked_ids = {a.id for a in articles}
    
    return templates.TemplateResponse("bookmarks.html", {
        "request": request,
        "articles": articles,
        "current_user": current_user,
        "bookmarked_ids": bookmarked_ids
    })
