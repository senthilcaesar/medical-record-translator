# Deployment Checklist for Medical Record Translator

## Pre-Deployment Checklist

### 1. Environment Variables Setup
Ensure you have all required environment variables:

- [ ] **OPENAI_API_KEY** - Your OpenAI API key with GPT-4 access
- [ ] **OPENAI_MODEL** - Set to `gpt-4o-2024-08-06`
- [ ] **CORS_ORIGINS** - Will be set after deployment
- [ ] **REDIS_URL** - Auto-configured by platform

### 2. Code Preparation

#### Backend Checklist:
- [ ] Remove `.env` file from git tracking
- [ ] Update `requirements.txt` with all dependencies
- [ ] Ensure `app.main:app` is the correct entry point
- [ ] Test locally with `uvicorn app.main:app --reload`
- [ ] Verify health endpoint works: `/api/v1/translate/health`

#### Frontend Checklist:
- [ ] Update `package.json` with correct build script
- [ ] Test production build locally: `npm run build`
- [ ] Verify no hardcoded API URLs in code
- [ ] Check that all assets are properly imported

### 3. Repository Setup
- [ ] Push all changes to GitHub
- [ ] Ensure repository is public or you have deployment permissions
- [ ] Create `.gitignore` with proper exclusions

## Railway.app Deployment Steps

### Step 1: Initial Setup (5 minutes)
1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub for easier integration
   - Verify your email

2. **Install Railway CLI** (Optional but recommended)
   ```bash
   npm install -g @railway/cli
   railway login
   ```

### Step 2: Create New Project
1. Click "New Project" in Railway dashboard
2. Select "Deploy from GitHub repo"
3. Choose your `medical-record-translator` repository
4. Railway will detect two services:
   - **Backend** (Python detected from requirements.txt)
   - **Frontend** (Node.js detected from package.json)

### Step 3: Configure Backend Service
1. Click on the backend service card
2. Go to "Variables" tab
3. Add the following:
   ```
   OPENAI_API_KEY=sk-...your-key-here
   OPENAI_MODEL=gpt-4o-2024-08-06
   PORT=8000
   CORS_ORIGINS=https://your-frontend.up.railway.app
   ```
4. Go to "Settings" tab:
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Health Check Path: `/api/v1/translate/health`
   - Root Directory: `/backend`

### Step 4: Add Redis Database
1. Click "New" → "Database" → "Redis"
2. Railway automatically injects `REDIS_URL` into your backend

### Step 5: Configure Frontend Service
1. Click on the frontend service card
2. Go to "Variables" tab
3. Add:
   ```
   VITE_API_URL=https://your-backend.up.railway.app
   NODE_ENV=production
   ```
4. Go to "Settings" tab:
   - Build Command: `npm install && npm run build`
   - Start Command: `npm run preview`
   - Root Directory: `/frontend`

### Step 6: Deploy
1. Railway automatically deploys when you save settings
2. Monitor the build logs for any errors
3. Once deployed, you'll get URLs like:
   - Backend: `https://medical-translator-api.up.railway.app`
   - Frontend: `https://medical-translator.up.railway.app`

### Step 7: Post-Deployment
1. Update backend's `CORS_ORIGINS` with your frontend URL
2. Test the application:
   - Visit your frontend URL
   - Upload a test PDF
   - Verify translation works

## Render.com Deployment Steps

### Step 1: Initial Setup (5 minutes)
1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up (GitHub integration recommended)
   - Verify your email

### Step 2: Create Services via Blueprint
1. In Render dashboard, click "New +" → "Blueprint"
2. Connect your GitHub repository
3. Render will read the `render.yaml` file
4. Review the services to be created:
   - Web Service (Backend)
   - Static Site (Frontend)
   - Redis

### Step 3: Configure Environment Variables
1. Go to the backend service
2. Navigate to "Environment" tab
3. Add:
   ```
   OPENAI_API_KEY=sk-...your-key-here
   ```
4. Other variables are auto-configured from `render.yaml`

### Step 4: Deploy
1. Click "Apply" to create all services
2. Monitor deployment in the dashboard
3. Services will be available at:
   - Backend: `https://medical-translator-api.onrender.com`
   - Frontend: `https://medical-translator.onrender.com`

## Quick Verification Tests

### 1. API Health Check
```bash
curl https://your-backend-url/api/v1/translate/health
```
Expected response:
```json
{"status": "healthy", "version": "1.0.0"}
```

### 2. Frontend Load Test
- Open frontend URL in browser
- Check console for any errors
- Verify "Upload" button is visible

### 3. End-to-End Test
1. Upload a small PDF file
2. Monitor progress bar
3. Verify translation appears
4. Check for any console errors

## Common Deployment Issues & Solutions

### Issue 1: CORS Errors
**Symptom**: "CORS policy" error in browser console
**Solution**: 
- Update `CORS_ORIGINS` in backend to match frontend URL
- Ensure no trailing slash in URLs
- Restart backend service

### Issue 2: File Upload Fails
**Symptom**: Upload starts but fails immediately
**Solution**:
- Check file size (must be under 10MB)
- Verify `/tmp` directory is writable
- Check backend logs for specific error

### Issue 3: OpenAI Timeout
**Symptom**: Translation takes too long and times out
**Solution**:
- Increase platform timeout (Railway: 5 min, Render: 15 min)
- Consider implementing progress updates
- Check OpenAI API status

### Issue 4: Redis Connection Failed
**Symptom**: "Redis connection refused" in logs
**Solution**:
- Verify REDIS_URL is set correctly
- Check Redis service is running
- Ensure internal networking is configured

## Performance Optimization Tips

### 1. Cold Start Optimization
- Keep at least 1 instance always running
- Use health check endpoints to keep warm
- Consider upgrading to paid tier for better performance

### 2. Cost Optimization
- Monitor OpenAI API usage in dashboard
- Implement caching for common translations
- Set up alerts for unusual usage

### 3. Scaling Preparation
- Monitor response times
- Set up error tracking (Sentry)
- Plan for database if user accounts needed

## Security Checklist

- [ ] Environment variables are not exposed in code
- [ ] HTTPS is enforced on both services
- [ ] File uploads are validated and size-limited
- [ ] Temporary files are auto-deleted
- [ ] No sensitive data in logs
- [ ] Rate limiting is enabled

## Monitoring Setup

### 1. Basic Monitoring (Free)
- Railway/Render built-in metrics
- Uptime monitoring with UptimeRobot
- Error notifications via email

### 2. Advanced Monitoring (Paid)
- Sentry for error tracking
- LogRocket for session replay
- DataDog for comprehensive metrics

## Next Steps After Deployment

1. **Custom Domain Setup**
   - Add your domain in platform settings
   - Update DNS records
   - Update CORS settings

2. **Backup Strategy**
   - Export environment variables
   - Document deployment process
   - Create staging environment

3. **User Feedback**
   - Add feedback form
   - Monitor usage patterns
   - Iterate based on user needs

## Emergency Procedures

### Service Down
1. Check platform status page
2. Review recent deployments
3. Rollback if needed
4. Check error logs

### High Traffic
1. Scale up instances
2. Enable caching
3. Implement queue system
4. Monitor costs

### API Key Compromised
1. Regenerate OpenAI API key immediately
2. Update environment variable
3. Restart services
4. Review access logs

## Support Resources

### Railway Support
- Documentation: [docs.railway.app](https://docs.railway.app)
- Discord: [discord.gg/railway](https://discord.gg/railway)
- Status: [status.railway.app](https://status.railway.app)

### Render Support
- Documentation: [render.com/docs](https://render.com/docs)
- Community: [community.render.com](https://community.render.com)
- Status: [status.render.com](https://status.render.com)

### OpenAI Support
- Documentation: [platform.openai.com/docs](https://platform.openai.com/docs)
- Status: [status.openai.com](https://status.openai.com)
- Usage: [platform.openai.com/usage](https://platform.openai.com/usage)

---

Remember: Both Railway and Render offer excellent free tiers perfect for getting started. You can have your medical record translator live in under 10 minutes! 🚀