from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    bookmarks = relationship("Bookmark", back_populates="user")

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    summary = Column(Text)
    url = Column(String)
    image_url = Column(String, nullable=True)
    category = Column(String, index=True)
    published_at = Column(DateTime)
    
    bookmarks = relationship("Bookmark", back_populates="article")

class Bookmark(Base):
    __tablename__ = "bookmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    article_id = Column(Integer, ForeignKey("articles.id"))
    
    user = relationship("User", back_populates="bookmarks")
    article = relationship("Article", back_populates="bookmarks")
