# Deployment Guide

## Backend (Render)

### Build Configuration
- **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- **Start Command:** `gunicorn config.wsgi:application`

### Environment Variables
```
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-backend.onrender.com,your-frontend.vercel.app,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
CSRF_TRUSTED_ORIGINS=https://your-backend.onrender.com,https://your-frontend.vercel.app,http://localhost:5173
USE_SQLITE=0
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your-database-name
DB_USER=your-database-user
DB_PASSWORD=your-database-password
DB_HOST=your-database-host
DB_PORT=5432
```

## Frontend (Vercel)

### Build Configuration
- **Framework Preset:** Vite
- **Root Directory:** frontend
- **Build Command:** `npm run build`
- **Output Directory:** dist

### Environment Variables
```
VITE_API_BASE_URL=https://your-backend.onrender.com/api
```

## Quick Start

1. Deploy backend to Render with the build command above
2. Set environment variables on Render
3. Deploy frontend to Vercel with `VITE_API_BASE_URL` pointing to your Render backend
4. Test the connection by accessing your Vercel URL