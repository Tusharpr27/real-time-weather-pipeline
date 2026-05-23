# Deployment Execution Guide

Get your Weather Data Pipeline live in production step-by-step.

---

## Pre-Deployment Checklist

Before deploying, verify everything is ready:

```bash
# ❌ DO NOT DEPLOY if any of these fail:

# 1. Check Git status
git status
# Should be clean (no uncommitted changes)

# 2. Run tests locally
npm run test          # Frontend
cd ../backend && python -m pytest  # Backend

# 3. Build locally (optional)
npm run build        # Frontend
python -m pytest --cov backend/  # Backend coverage

# 4. Verify Docker files exist
test -f frontend/Dockerfile && echo "✅ Frontend Dockerfile"
test -f backend/Dockerfile && echo "✅ Backend Dockerfile"
test -f nginx/nginx.conf && echo "✅ Nginx config"
test -f docker-compose.yml && echo "✅ Docker Compose"

# 5. Verify GitHub Actions workflows
test -f .github/workflows/backend-ci.yml && echo "✅ Backend CI"
test -f .github/workflows/frontend-ci.yml && echo "✅ Frontend CI"
test -f .github/workflows/deploy.yml && echo "✅ Deploy workflow"

# 6. Verify environment templates
test -f .env.backend.example && echo "✅ Backend env template"
test -f .env.frontend.example && echo "✅ Frontend env template"
```

All should be ✅. If any fail, fix before proceeding.

---

## Step 1: Set Up GitHub Secrets (15 minutes)

### 1.1 Generate Deployment Token

```bash
# Generate secure random token
openssl rand -hex 32
# Copy output: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 1.2 Choose Deployment Platform

Options:
- **Railway.app** (Recommended: easiest)
- **Render.com** (Free tier)
- **Fly.io** (Global)
- **DigitalOcean** (Scalable)
- **Custom Server** (Full control)

See [CLOUD_DEPLOYMENT_PLATFORMS.md](./CLOUD_DEPLOYMENT_PLATFORMS.md) for details.

### 1.3 Get Deployment Webhook URLs

**Railway Example:**
1. Log in to Railway dashboard
2. Go to your project
3. Click service
4. **Settings** → **Deploy Hooks**
5. Create hook → Copy URL

Example format:
```
https://api.railway.app/webhooks/deploy/xxxxx?token=yyyy
```

**Render Example:**
1. Log in to Render dashboard
2. Go to your service
3. **Settings** → **Deploy Hooks**
4. Copy the webhook URL

### 1.4 Add Secrets to GitHub

1. Go to GitHub repository
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these secrets:

**Secret 1: DEPLOY_TOKEN**
- Value: The token from step 1.1

**Secret 2: PROD_DEPLOY_URL**
- Value: Webhook URL from step 1.3

**Secret 3: STAGING_DEPLOY_URL** (Optional)
- Value: Staging webhook URL (if using staging)

### 1.5 Verify Secrets Added

Click on each secret name to confirm it appears (without showing value).

---

## Step 2: Prepare Environment (10 minutes)

### 2.1 Create Backend Environment File

On your deployment server or platform:

```bash
# Copy template
cp .env.backend.example .env.backend

# Edit with actual values
nano .env.backend  # or your editor

# Required values to set:
DATABASE_URL=postgresql://user:pass@host:5432/weather
REDIS_URL=redis://:password@host:6379
SECRET_KEY=your-secret-key-here  # Use: openssl rand -hex 32
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
CORS_ORIGINS=https://your-frontend-domain.com,http://localhost:3000
API_TITLE=Weather Data Pipeline
LOG_LEVEL=INFO
SENTRY_ENVIRONMENT=production
```

### 2.2 Create Frontend Environment File

On your deployment server:

```bash
# Copy template
cp .env.frontend.example .env.frontend

# Edit with actual values
nano .env.frontend

# Required values to set:
VITE_API_BASE_URL=https://your-api-domain.com/api
VITE_API_TIMEOUT=30000
VITE_ENABLE_OFFLINE_MODE=true
VITE_ENABLE_PWA=true
VITE_WEBSOCKET_URL=wss://your-api-domain.com/ws
VITE_SENTRY_ENVIRONMENT=production
VITE_LOG_LEVEL=info
```

### 2.3 Set Platform-Specific Variables

**If using Railway:**

Via Railway dashboard:
1. Click Backend service
2. **Variables** tab
3. Paste each line from .env.backend
4. Repeat for Frontend

**If using Render:**

Via Render dashboard:
1. Click service
2. **Environment**
3. Add environment variables from files

**If using custom server:**

```bash
# Copy files to server
scp .env.backend deploy@server.com:/home/deploy/
scp .env.frontend deploy@server.com:/home/deploy/
```

---

## Step 3: Test CI/CD Locally (Optional)

If you have Docker installed elsewhere (Colima, Rancher, Podman):

```bash
# Build backend
docker build -t weather-backend:test -f backend/Dockerfile .

# Build frontend
docker build -t weather-frontend:test -f frontend/Dockerfile .

# Test they run
docker run -p 8000:8000 weather-backend:test &
docker run -p 3000:3000 weather-frontend:test &

# Check health
curl http://localhost:8000/health
curl http://localhost:3000/health

# Cleanup
docker stop $(docker ps -q)
```

All should return 200 OK.

---

## Step 4: Push Code to GitHub

This triggers the GitHub Actions CI/CD pipeline.

### 4.1 Commit Changes

```bash
# Stage all files
git add .

# Verify changes
git status

# Commit with message
git commit -m "Phase 2.8: Deployment and CI/CD setup"

# Example of other commit messages:
# git commit -m "Docker: Add production Dockerfile"
# git commit -m "CI/CD: Add GitHub Actions workflows"
# git commit -m "Config: Add environment templates"
```

### 4.2 Push to GitHub

```bash
# Push to main branch (triggers GitHub Actions)
git push origin main

# Or push to develop for staging
git push origin develop
```

### 4.3 Watch GitHub Actions

1. Go to GitHub repository
2. Click **Actions** tab
3. See workflow running
4. Click on workflow to see details

**You should see:**
- Backend CI running (lint → test → security → build)
- Frontend CI running (lint → test → build → lighthouse)
- Logs scrolling in real-time

Wait for both to complete (usually 5-10 minutes).

---

## Step 5: Verify GitHub Actions Pass

### 5.1 Check Backend CI

In GitHub Actions:
1. Click **backend-ci** workflow
2. Scroll down to see results

Should see:
- ✅ Lint passed
- ✅ Test passed
- ✅ Security passed
- ✅ Image pushed to ghcr.io

If any ❌ fails:
1. Click failed job
2. Read error message
3. Fix in local code
4. Commit and push again

### 5.2 Check Frontend CI

Similar checks for frontend:
- ✅ Lint passed
- ✅ Type check passed
- ✅ Test passed
- ✅ Image pushed to ghcr.io

### 5.3 Verify Images in Registry

```bash
# View pushed images (GitHub Container Registry)
# Go to: github.com/yourusername?tab=packages

# Or via command line:
curl -X GET \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/users/yourusername/packages/container/weather-backend/versions
```

---

## Step 6: Deploy to Staging (Optional)

If using staging environment:

```bash
# Push to develop branch (triggers staging deploy)
git push origin develop
```

Check staging deployment:
1. GitHub Actions runs deploy workflow
2. Calls staging webhook
3. Platform deploys new version
4. Health checks verify success

Monitor logs for errors.

---

## Step 7: Deploy to Production

### 7.1 Create Release Tag

Create a version tag to trigger production deployment:

```bash
# Tag current commit (e.g., v1.0.0)
git tag v1.0.0

# Push tag to GitHub
git push origin v1.0.0
```

**This automatically:**
1. Triggers GitHub Actions
2. Builds final Docker images
3. Calls production webhook
4. Deploys to production
5. Runs health checks

### 7.2 Alternative: Deploy from Main

Or push directly to main:

```bash
# Verify everything is ready
git log --oneline -5

# Push to main (triggers prod deploy)
git push origin main
```

### 7.3 Monitor Deployment

In GitHub Actions:
1. Click **deploy** workflow
2. Watch status scroll by
3. See health check results

**Successful deployment shows:**
```
✅ Deployment created
✅ Calling webhook: PROD_DEPLOY_URL
✅ Health check attempt 1/10... OK
✅ Deployment status: success
```

---

## Step 8: Verify Production Deployment

### 8.1 Test API Endpoint

```bash
# Get your production domain
# Replace with your actual domain

curl https://your-weather-api.com/health
# Expected: {"status": "healthy"}

# Test API endpoint
curl https://your-weather-api.com/api/weather?city=New%20York
# Expected: Weather data JSON response

# Test WebSocket (requires wscat)
npm install -g wscat
wscat -c wss://your-weather-api.com/ws
# Type: {"action": "subscribe", "data": {"city": "NYC"}}
```

### 8.2 Test Frontend

1. Open browser
2. Go to: `https://your-weather-frontend.com`
3. Should load without errors
4. Navigate to different pages
5. Check browser console (F12) for errors

### 8.3 Test Real-Time Features

1. Open app in 2 browser tabs
2. Subscribe to a location in both
3. Verify updates appear in real-time
4. Check network tab for WebSocket connection

### 8.4 Test Offline Mode

1. Open app in browser
2. Go to DevTools (F12)
3. Network tab → Online → Offline
4. Verify app still functions
5. Click back online

### 8.5 Test PWA (Installable)

1. Open app in Chromium browser
2. Address bar → "Install" option should appear
3. Click install
4. Verify appears on home screen

---

## Step 9: Post-Deployment Setup

### 9.1 Monitor Logs

Set up log monitoring:

```bash
# Railway
railway logs -f

# Render
# Check via dashboard

# Custom server
docker logs -f backend-container
docker logs -f frontend-container
docker logs -f nginx-container
```

### 9.2 Monitor Errors

Watch Sentry for errors (if configured):

1. Go to [sentry.io](https://sentry.io)
2. Select your project
3. Should see errors from production
4. Fix issues and redeploy

### 9.3 Check Performance

Verify performance metrics:

```bash
# Check page load time
curl -w "Time: %{time_total}s\n" https://your-frontend.com

# Check API response time
time curl https://your-api.com/api/health

# Should be < 200ms for API, < 3s for frontend
```

### 9.4 Configure Alerts

Set up alerts for issues:

**Email Alerts:**
1. Platform dashboard
2. Settings → Alerts
3. Configure email on deployment failure

**Slack Alerts:**
1. Create Slack webhook
2. Add to GitHub Actions notification
3. Get alerts in Slack

### 9.5 Enable Auto-Scaling

If your platform supports it:

1. Platform dashboard
2. Service settings
3. Enable auto-scaling if traffic spikes
4. Set resource limits

---

## Troubleshooting First Deployment

### Issue: GitHub Actions Says "Invalid"

**Problem:** Workflow syntax error

**Solution:**
1. Check YAML indentation
2. Verify secret names match (case-sensitive)
3. Re-run workflow: Actions tab → Re-run jobs

### Issue: Docker Image Push Failed

**Problem:** Authorization error to ghcr.io

**Solution:**
1. Verify GITHUB_TOKEN has `write:packages` scope
2. Wait a few minutes, retry
3. Check GitHub status page

### Issue: Deployment Webhook Not Called

**Problem:** deploy.yml not triggering

**Solution:**
1. Check `on:` triggers in deploy.yml
2. Verify tag format is `vX.Y.Z` for releases
3. Manually trigger: Actions tab → Deploy workflow → Run

### Issue: Health Checks Failing

**Problem:** /health endpoint returns error

**Solution:**
1. Check logs for startup errors
2. Verify environment variables set correctly
3. Check database connectivity
4. Verify port is exposed

### Issue: Frontend Shows Blank Page

**Problem:** Build not completed or wrong base URL

**Solution:**
1. Check browser console (F12) for errors
2. Verify `VITE_API_BASE_URL` in frontend environment
3. Check network tab for failed requests
4. Rebuild and redeploy

### Issue: API Calls Return 503

**Problem:** Backend not responding

**Solution:**
1. Check backend logs
2. Verify database service running
3. Check Redis service status
4. Restart services

---

## Rollback Procedure

If something goes wrong in production:

### Option 1: Revert Last Deployment

```bash
# Go to previous commit
git revert HEAD

# Or checkout previous version
git checkout v1.0.0

# Push (triggers new deployment)
git push origin main
```

### Option 2: Manual Rollback

If using Railway/Render:
1. Dashboard → Deployments
2. Click previous successful deployment
3. Click "Redeploy"
4. Confirms automatic redeployment

### Option 3: Switch Traffic

If using blue-green deployment:
1. Keep previous version running
2. Switch load balancer to old version
3. Debug new version separately
4. Switch back when fixed

---

## Ongoing Maintenance

### Weekly Tasks

- [ ] Check application logs for errors
- [ ] Monitor uptime/performance
- [ ] Review and update dependencies
- [ ] Test critical flows manually

### Monthly Tasks

- [ ] Rotate secrets
- [ ] Update base Docker images
- [ ] Review and update security headers
- [ ] Audit access logs
- [ ] Test disaster recovery

### Quarterly Tasks

- [ ] Full security audit
- [ ] Performance optimization
- [ ] Database maintenance
- [ ] Capacity planning

---

## Victory Checklist

Celebrate when you have ✅:

- ✅ Code pushed to GitHub
- ✅ GitHub Actions CI/CD passed
- ✅ Docker images built and pushed
- ✅ Production deployment successful
- ✅ Health checks passing
- ✅ Frontend loads in browser
- ✅ API responds with data
- ✅ Real-time updates working
- ✅ Logs show no critical errors
- ✅ Monitoring configured

**Your Weather Data Pipeline is LIVE! 🚀**

---

## What's Next?

After successful deployment:

1. **Promote to Team:**
   - Share deployment links
   - Gather user feedback
   - Document known issues

2. **Scale if Needed:**
   - Monitor resource usage
   - Increase instance size if needed
   - Add load balancing

3. **Enhance Features:**
   - Add more weather data sources
   - Implement user accounts
   - Add data export functionality

4. **Optimize:**
   - Profile performance
   - Optimize database queries
   - Compress assets further

5. **Secure:**
   - Run security audit
   - Enable WAF if available
   - Implement rate limiting

---

## Support

Having issues? Check:

1. [Phase 2.8 Deployment Documentation](./PHASE_2.8_DEPLOYMENT_CI_CD.md)
2. [GitHub Secrets Setup](./GITHUB_SECRETS_SETUP.md)
3. [Cloud Platform Guides](./CLOUD_DEPLOYMENT_PLATFORMS.md)
4. Platform documentation
5. GitHub Actions logs

---

**Deployment complete! Your app is now live! 🎉**
