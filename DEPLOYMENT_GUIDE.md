# Deployment Guide: Frontend (Vercel) + Backend (Render)

This guide explains how to deploy and connect your React frontend on Vercel with your Django backend on Render.

## Step 1: Deploy Backend to Render

1. **Push your code to GitHub** (if not already done)

2. **Create a new Web Service on Render:**
   - Go to [render.com](https://render.com) and sign in
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure the Render service:**
   - **Name:** `utility-dashboard-backend` (or your preferred name)
   - **Region:** Choose closest to your users
   - **Branch:** `main` (or your deployment branch)
   - **Root Directory:** (leave blank)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn config.wsgi:application`

4. **Set Environment Variables on Render:**
   ```
   SECRET_KEY=your-production-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=your-backend-url.onrender.com,your-frontend-url.vercel.app
   CORS_ALLOWED_ORIGINS=https://your-frontend-url.vercel.app
   USE_SQLITE=0
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=your-database-name
   DB_USER=your-database-user
   DB_PASSWORD=your-database-password
   DB_HOST=your-database-host
   DB_PORT=5432
   ```

5. **Deploy** - Render will build and deploy your backend
   - Note your backend URL (e.g., `https://utility-dashboard-backend.onrender.com`)

## Step 2: Configure Frontend for Vercel

1. **Update frontend environment variables:**
   
   Create a `.env.production` file in the `frontend/` directory:
   ```
   VITE_API_BASE_URL=https://your-backend-url.onrender.com/api
   ```

2. **Update `frontend/.env.example`:**
   ```
   VITE_API_BASE_URL=https://your-backend-url.onrender.com/api
   ```

3. **Update `frontend/src/api/client.js`** (already configured to use `VITE_API_BASE_URL`)

## Step 3: Deploy Frontend to Vercel

1. **Push your code to GitHub** (if not already done)

2. **Import project to Vercel:**
   - Go to [vercel.com](https://vercel.com) and sign in
   - Click "Add New..." → "Project"
   - Import your GitHub repository

3. **Configure Vercel project:**
   - **Framework Preset:** `Vite`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

4. **Set Environment Variables on Vercel:**
   ```
   VITE_API_BASE_URL=https://your-backend-url.onrender.com/api
   ```

5. **Deploy** - Vercel will build and deploy your frontend
   - Note your frontend URL (e.g., `https://your-project.vercel.app`)

## Step 4: Update Backend CORS Settings

After deploying the frontend, update the backend's CORS settings on Render:

1. **Go to Render dashboard** → Your backend service → Environment

2. **Add/Update these environment variables:**
   ```
   CORS_ALLOWED_ORIGINS=https://your-frontend-url.vercel.app,http://localhost:5173
   ALLOWED_HOSTS=your-backend-url.onrender.com,your-frontend-url.vercel.app,localhost,127.0.0.1
   ```

3. **Redeploy** the backend to apply changes

## Step 5: Update Django Settings (Optional but Recommended)

Update `config/settings.py` to read CORS settings from environment variables:

```python
# CORS Settings - Read from environment variable
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:5173').split(',')

# Allow credentials if needed
CORS_ALLOW_CREDENTIALS = True

# Allowed hosts from environment
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

## Testing the Connection

1. **Open your Vercel frontend URL** in a browser
2. **Try to log in** or access any API endpoint
3. **Check browser console** for any CORS errors
4. **Check Render logs** for any backend errors

## Troubleshooting

### CORS Errors
If you see CORS errors in the browser console:
1. Verify `CORS_ALLOWED_ORIGINS` on Render includes your Vercel URL
2. Check that `ALLOWED_HOSTS` includes your Vercel domain
3. Ensure the frontend is using the correct backend URL

### API Connection Issues
If the frontend can't connect to the backend:
1. Verify `VITE_API_BASE_URL` is set correctly on Vercel
2. Check that the backend is running (visit the backend URL directly)
3. Check Render logs for any errors

### Database Issues
If you're using PostgreSQL on Render:
1. Add PostgreSQL database from Render dashboard
2. Copy the internal database URL to environment variables
3. Set `USE_SQLITE=0` and configure PostgreSQL settings

## Summary of URLs

| Component | URL Format | Example |
|-----------|------------|---------|
| Backend API | `https://your-backend.onrender.com/api` | `https://utility-backend.onrender.com/api` |
| Frontend | `https://your-project.vercel.app` | `https://utility-dashboard.vercel.app` |

## Environment Variables Summary

### Backend (Render):
- `SECRET_KEY` - Django secret key
- `DEBUG=False` - Production mode
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of allowed origins
- `USE_SQLITE=0` - Use PostgreSQL instead of SQLite
- Database credentials (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`)

### Frontend (Vercel):
- `VITE_API_BASE_URL` - Backend API URL (without trailing slash)