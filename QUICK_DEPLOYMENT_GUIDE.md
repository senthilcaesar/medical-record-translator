# Quick Deployment Guide: Railway.app & Render.com

## Option 1: Railway.app (Recommended for Simplicity)

Railway provides the easiest deployment experience with automatic builds, SSL, and database provisioning.

### Prerequisites
- GitHub account with your code repository
- Railway account (free tier available)
- OpenAI API key

### Step-by-Step Railway Deployment

#### 1. Prepare Your Repository

First, create a `railway.json` in your root directory:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 2. Create Backend Configuration

Create `backend/railway.toml`:

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/v1/translate/health"
healthcheckTimeout = 30
restartPolicyType = "on-failure"
restartPolicyMaxRetries = 3
```

#### 3. Update Backend for Railway

Create `backend/Procfile`:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Update `backend/app/config.py` to use environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Configuration
    API_V1_STR = "/api/v1"
    PROJECT_NAME = "Medical Record Translator"
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-2024-08-06")
    
    # File Upload Configuration
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {".pdf"}
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    
    # Security
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Redis Configuration (Railway provides Redis)
    REDIS_URL = os.getenv("REDIS_URL", "")
    JOB_EXPIRY = 3600  # 1 hour
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = 10
    
    # Railway automatically sets PORT
    PORT = int(os.getenv("PORT", 8000))

settings = Settings()
```

#### 4. Deploy to Railway

1. **Via GitHub Integration (Easiest)**:
   ```bash
   # Push your code to GitHub
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **In Railway Dashboard**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect your services

3. **Configure Services**:
   Railway will create two services automatically:
   - `backend` (Python/FastAPI)
   - `frontend` (Node.js/React)

4. **Add Environment Variables**:
   Click on the backend service and add:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o-2024-08-06
   CORS_ORIGINS=https://your-frontend.up.railway.app
   ```

5. **Add Redis Database**:
   - Click "New" → "Database" → "Add Redis"
   - Railway automatically sets REDIS_URL

6. **Configure Frontend**:
   Click on the frontend service and add:
   ```
   VITE_API_URL=https://your-backend.up.railway.app
   ```

7. **Deploy**:
   - Railway automatically builds and deploys on every push
   - Get your URLs from the service settings

### Railway Deployment Script

Create `deploy-railway.sh`:

```bash
#!/bin/bash

echo "🚂 Deploying to Railway..."

# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Create new project
railway init

# Link to your repo
railway link

# Deploy backend
cd backend
railway up

# Deploy frontend
cd ../frontend
railway up

echo "✅ Deployment complete!"
echo "🔗 Check your Railway dashboard for URLs"
```

---

## Option 2: Render.com

Render offers more control with clear pricing and good performance.

### Step-by-Step Render Deployment

#### 1. Prepare Configuration Files

Create `render.yaml` in root directory:

```yaml
services:
  # Backend API Service
  - type: web
    name: medical-translator-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    rootDir: backend
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: OPENAI_API_KEY
        sync: false  # Add via dashboard
      - key: OPENAI_MODEL
        value: gpt-4o-2024-08-06
      - key: REDIS_URL
        fromService:
          type: redis
          name: medical-translator-redis
          property: connectionString
      - key: CORS_ORIGINS
        value: https://medical-translator.onrender.com
    autoDeploy: true

  # Frontend Service
  - type: web
    name: medical-translator-frontend
    env: static
    buildCommand: "npm install && npm run build"
    staticPublishPath: ./dist
    rootDir: frontend
    envVars:
      - key: VITE_API_URL
        value: https://medical-translator-api.onrender.com
    headers:
      - path: /*
        name: X-Frame-Options
        value: DENY
      - path: /*
        name: X-Content-Type-Options
        value: nosniff
    routes:
      - type: rewrite
        source: /*
        destination: /index.html

  # Redis Database
  - type: redis
    name: medical-translator-redis
    ipAllowList: []  # Allow only internal connections
    maxmemoryPolicy: allkeys-lru
    plan: free
```

#### 2. Update Frontend for Production

Create `frontend/.env.production`:

```env
VITE_API_URL=https://medical-translator-api.onrender.com
```

Update `frontend/vite.config.js`:

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    }
  }
})
```

#### 3. Deploy to Render

1. **Via GitHub**:
   ```bash
   git add .
   git commit -m "Add Render configuration"
   git push origin main
   ```

2. **In Render Dashboard**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will read `render.yaml` and create all services

3. **Add Secret Environment Variables**:
   - Go to the backend service
   - Add `OPENAI_API_KEY` in Environment section

4. **Custom Domain** (Optional):
   - Add your domain in Settings → Custom Domains
   - Update CORS_ORIGINS accordingly

---

## Quick Comparison

| Feature | Railway | Render |
|---------|---------|---------|
| **Setup Time** | ~5 minutes | ~10 minutes |
| **Free Tier** | $5 credit/month | 750 hours/month |
| **Auto-scaling** | Yes | Manual |
| **SSL Certificates** | Automatic | Automatic |
| **Custom Domains** | Free | Free |
| **Redis Included** | Yes | Yes |
| **GitHub Integration** | Excellent | Excellent |
| **Build Speed** | Very Fast | Fast |
| **Logs** | Real-time | Real-time |
| **CLI Available** | Yes | Yes |

---

## Post-Deployment Checklist

### 1. Test Your Deployment
```bash
# Test API health
curl https://your-backend-url/api/v1/translate/health

# Test frontend
open https://your-frontend-url
```

### 2. Monitor Performance
Both platforms provide:
- Real-time logs
- Metrics dashboard
- Uptime monitoring
- Error alerts

### 3. Set Up Error Tracking (Optional)

Add Sentry for production error tracking:

```python
# backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment="production",
        traces_sample_rate=0.1,
    )
    app.add_middleware(SentryAsgiMiddleware)
```

### 4. Enable Auto-Deploy

Both platforms support automatic deployment on git push:
- Railway: Automatic by default
- Render: Enable in service settings

---

## Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Update `CORS_ORIGINS` in backend environment
   - Ensure frontend URL is correct

2. **File Upload Fails**:
   - Check `/tmp` directory permissions
   - Verify file size limits

3. **OpenAI Timeout**:
   - Increase timeout in platform settings
   - Railway: Set in `railway.toml`
   - Render: Set in service settings

4. **Redis Connection**:
   - Verify REDIS_URL is set correctly
   - Check Redis service is running

### Quick Fixes

```bash
# Railway - Restart service
railway restart

# Render - Trigger manual deploy
render deploy --service medical-translator-api

# Check logs
railway logs
# or
render logs --service medical-translator-api --tail
```

---

## Next Steps

1. **Add Custom Domain**:
   - Both platforms support free custom domains
   - Update CORS settings after domain change

2. **Scale Up**:
   - Railway: Adjust replicas in dashboard
   - Render: Upgrade to paid plan for auto-scaling

3. **Add Monitoring**:
   - Set up uptime monitoring (UptimeRobot)
   - Configure error alerts
   - Track API usage

4. **Optimize Costs**:
   - Monitor usage in dashboard
   - Set up caching to reduce API calls
   - Implement request queuing for heavy loads

---

## One-Command Deploy Scripts

### Railway Quick Deploy
```bash
curl -sSL https://raw.githubusercontent.com/your-repo/main/scripts/deploy-railway.sh | bash
```

### Render Quick Deploy
```bash
curl -sSL https://raw.githubusercontent.com/your-repo/main/scripts/deploy-render.sh | bash
```

Choose Railway for the absolute simplest deployment, or Render for more control and better free tier limits. Both will have your app live in under 10 minutes! 🚀