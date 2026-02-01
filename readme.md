# Daily News Web App

A production-ready daily news application built with Python and FastAPI, designed for ~10 users with zero hosting costs.

## Features

- 📰 Automated news fetching from Google News RSS feeds
- 🎨 AI-generated unique images for each article (DALL-E 3)
- 🔐 Secure user authentication with email and password
- 🔖 Bookmark favorite articles
- 📱 Responsive design
- ⚡ Fast, cached content delivery

## Tech Stack

- **Backend**: FastAPI, Python 3.11
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Jinja2 templates, Tailwind CSS (CDN)
- **Authentication**: Passlib with bcrypt
- **News Source**: Google News RSS (feedparser)
- **Scheduler**: APScheduler
- **Hosting**: Render (Free Web Service)

## Project Structure

```
news_app/
│
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and RSS feed URLs
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── scheduler.py         # Background news fetching
│   ├── auth/
│   │   └── routes.py        # Authentication routes
│   └── news/
│       ├── routes.py        # News and bookmark routes
│       └── rss.py           # RSS feed parsing
│
├── templates/               # Jinja2 HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── index.html
│   └── bookmarks.html
│
├── static/
│   └── styles.css          # Custom CSS
│
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Database Schema

### users
- id (PK)
- email (unique)
- password_hash
- created_at

### articles
- id (PK)
- title
- summary
- url
- image_url (nullable)
- category
- published_at

### bookmarks
- id (PK)
- user_id (FK → users.id)
- article_id (FK → articles.id)

## News Categories

- Technology
- Business
- Sports
- Health

## Local Development

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Add default image** (optional):
Place a `default-news.jpg` file in the `static/` folder. Note: This is only used as a visual reference. The application requires OpenAI API for image generation.

3. **Set OpenAI API Key** (REQUIRED):
```bash
export OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
```

4. **Run the application**:
```bash
uvicorn app.main:app --reload
```

5. **Access the app**:
Open http://localhost:8000 in your browser

## Deployment to Render

1. **Create a new Web Service** on Render
2. **Connect your GitHub repository**
3. **Configure the service**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
4. **Add environment variables**:
   - `SECRET_KEY`: A secure random string (required)
   - `OPENAI_API_KEY`: Your OpenAI API key for AI image generation (required)

5. **Deploy**: Render will automatically deploy your app

## How It Works

1. **News Fetching**: The app fetches news from Google News RSS feeds every 12 hours using APScheduler
2. **AI Image Generation**: Articles without RSS images get unique AI-generated images based on headlines using OpenAI DALL-E 3
3. **Storage**: Articles and generated image URLs are cached in SQLite to avoid refetching
4. **Authentication**: Users register with email/password, sessions managed via HTTP-only cookies
5. **Bookmarks**: Users can bookmark articles for later reading

## Security Features

- Passwords hashed with bcrypt
- HTTP-only cookies for session management
- HTTPS via Render's default SSL
- No sensitive data in frontend

## Limitations

- Designed for ~10 concurrent users
- SQLite database (suitable for low traffic)
- No external cron required (built-in scheduler)

## Cost

- **Hosting**: $0 (Render free tier)
- **OpenAI API**: Pay-as-you-go (~$0.20-$1.60 per 12-hour cycle)
  - Most articles use RSS images (free)
  - AI generation only for articles without images
  - See `OPENAI_SETUP.md` for details

## Notes

- News is fetched automatically on startup and every 12 hours
- AI images are generated once per article and cached permanently
- **OpenAI API key required** - see `OPENAI_SETUP.md` for configuration
- SQLite database file is stored locally on the server
- No API keys required for Google News RSS feeds
- Mobile-responsive design using Tailwind CSS
- Article cards display: Category, Headline, Date, and "Read more" link only

## License

This project is built according to specification for educational purposes.