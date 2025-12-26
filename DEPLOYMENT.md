# Deployment Guide

## Web Version Deployment

The game has been built as a web application that can be deployed to cloud platforms like Render or Vercel.

### Architecture

- **Backend**: Flask web server (`app.py`)
- **Frontend**: HTML5 Canvas + JavaScript (`templates/index.html`, `static/game.js`)
- **Game Logic**: Python modules in `game/` directory (reused from desktop version)

### Prerequisites

- GitHub account
- Render or Vercel account (free tier works)

## Deploy to Render

Render is recommended for this game because it supports Python web services natively and provides persistent storage.

### Step-by-Step Guide

1. **Fork the Repository**
   - Go to https://github.com/camkilo/onebreathleft
   - Click "Fork" to create your own copy

2. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub (recommended)

3. **Create New Web Service**
   - Click "New +" in the top right
   - Select "Web Service"
   - Choose "Connect a repository"
   - Authorize Render to access your GitHub
   - Select your forked `onebreathleft` repository

4. **Configure Service**
   - Render will auto-detect the `render.yaml` configuration
   - Or manually configure:
     - **Name**: onebreathleft (or your choice)
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements-web.txt`
     - **Start Command**: `gunicorn app:app`
     - **Instance Type**: Free

5. **Add Environment Variable**
   - In the service settings, add:
     - Key: `SECRET_KEY`
     - Value: (click "Generate" for a secure random key)

6. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your app
   - Wait 2-3 minutes for deployment
   - Your game will be live at: `https://your-app-name.onrender.com`

### Render Free Tier Notes

- Service spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- Playthrough data persists between restarts
- Sufficient for personal use and demos

## Deploy to Vercel

Vercel is optimized for static sites and serverless functions. It's fast but has limitations for Python applications.

### Step-by-Step Guide

1. **Fork the Repository**
   - Go to https://github.com/camkilo/onebreathleft
   - Click "Fork" to create your own copy

2. **Create Vercel Account**
   - Go to https://vercel.com
   - Sign up with GitHub (recommended)

3. **Import Project**
   - Click "Add New..." → "Project"
   - Select your forked repository
   - Vercel will auto-detect `vercel.json`

4. **Configure**
   - **Framework Preset**: Other
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
   - Vercel uses the `vercel.json` configuration

5. **Environment Variables**
   - Add environment variable:
     - Key: `SECRET_KEY`
     - Value: (generate a random 32-character string)

6. **Deploy**
   - Click "Deploy"
   - Wait 1-2 minutes
   - Your game will be live at: `https://your-app.vercel.app`

### Vercel Limitations

- Serverless functions have 10-second timeout on free tier
- No persistent storage (playthrough data resets)
- Better for demo purposes than extended play

## Deploy to Other Platforms

### Heroku

```bash
# Install Heroku CLI
# Login: heroku login

# Create app
heroku create your-app-name

# Add buildpack
heroku buildpacks:set heroku/python

# Deploy
git push heroku main

# Set secret key
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
```

### Railway

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Python and uses `Procfile`
5. Add `SECRET_KEY` environment variable
6. Deploy

### Local Development

```bash
# Install dependencies
pip install -r requirements-web.txt

# Run development server
python app.py

# Or with gunicorn (production-like)
gunicorn app:app

# Open http://localhost:5000
```

## Testing Deployment

After deployment, verify these features:

1. **Game Loads**: Canvas renders with dark background
2. **Movement**: WASD keys move player
3. **Stats**: Health/stamina/fear bars update
4. **Enemies**: Abstract shapes spawn periodically
5. **AI Advice**: Message appears in box at bottom
6. **Trust System**: Y/N keys affect trust meter
7. **Endings**: Game ends and shows statistics
8. **Persistence**: Second playthrough loads previous data

## Troubleshooting

### "Module not found" errors
- Check `requirements-web.txt` is complete
- Ensure build command installs dependencies
- Verify Python version is 3.11+

### Game doesn't load
- Check browser console for JavaScript errors
- Verify Flask server is running (check logs)
- Test `/api/health` endpoint

### Playthrough data not persisting
- On Vercel: Expected (serverless limitation)
- On Render: Check service didn't restart
- Verify `playthroughs/` directory exists

### Slow performance
- Render free tier: Expected on first load
- Check browser DevTools Network tab
- Ensure API calls complete successfully

## Custom Domain

### Render
1. Go to service Settings → Custom Domains
2. Add your domain
3. Update DNS records as instructed

### Vercel
1. Go to project Settings → Domains
2. Add your domain
3. Update DNS records as instructed

## Monitoring

### Render
- View logs: Dashboard → Your Service → Logs
- Monitor metrics: CPU, memory, requests

### Vercel
- View logs: Project → Deployments → View Deployment → Functions
- Analytics available on Pro plan

## Scaling

For production use with many players:

1. **Use Redis** for session storage instead of in-memory dict
2. **Add PostgreSQL** for persistent playthrough storage
3. **Enable Caching** for static assets
4. **Use CDN** for global distribution
5. **Upgrade Tier** for guaranteed uptime and resources

## Security Notes

- `SECRET_KEY` must be set in production
- CORS is enabled for API endpoints
- No authentication implemented (add if needed)
- Playthrough data is not encrypted (contains no PII)

## Cost Estimates

### Free Tier (Personal Use)
- **Render**: Free (750 hours/month)
- **Vercel**: Free (100 GB bandwidth/month)
- **Railway**: Free ($5 credit/month)

### Paid Tier (Production)
- **Render**: $7/month (Starter)
- **Vercel**: $20/month (Pro)
- **Railway**: $5/month (pay as you go)

## Support

- Issues: https://github.com/camkilo/onebreathleft/issues
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
