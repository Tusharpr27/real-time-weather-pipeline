# Cloud Platform Deployment Guides

This guide covers deploying the Weather Data Pipeline to popular cloud platforms without requiring Docker Desktop locally.

---

## Platform Comparison

| Platform | Free Tier | Container Support | GitHub Integration | Learning Curve |
|----------|-----------|------------------|-------------------|-----------------|
| **Railway** | $5/month credits | ✅ Docker | ✅ Native | 🟢 Easy |
| **Render** | ✅ Always free tier | ✅ Docker | ✅ Native | 🟢 Easy |
| **Fly.io** | ✅ Free tier | ✅ Docker | ✅ Via CLI | 🟡 Medium |
| **Heroku** | ❌ Paid only | ✅ Docker | ✅ Native | 🟢 Easy |
| **AWS ECS** | ❌ Paid | ✅ Docker | ✅ Via CloudFormation | 🔴 Complex |
| **DigitalOcean** | ❌ Paid ($5/mo) | ✅ Docker | ✅ Via Marketplace | 🟡 Medium |
| **Vercel** | ✅ Free tier | ✅ (Frontend only) | ✅ Native | 🟢 Easy |

---

## Railway.app (Recommended for Beginners)

Railway is the easiest path for full-stack deployment with persistent free credits ($5/month).

### Pros
- ✅ Free $5/month credit (can run full stack)
- ✅ Beautiful dashboard
- ✅ Automatic GitHub syncing
- ✅ Built-in PostgreSQL & Redis
- ✅ Pull request environments
- ✅ Excellent documentation

### Cons
- ❌ After free credit expires, need to pay ($5/month minimum)
- ❌ Limited to US regions

### Setup Steps

#### 1. Create Railway Account

1. Visit [railway.app](https://railway.app)
2. Click **Start Project**
3. Sign in with GitHub
4. Authorize Railway access

#### 2. Create New Project

1. Click **+ New Project**
2. Select **Deploy from GitHub repo**
3. Select your repository
4. Click **Deploy**

#### 3. Add Database Services

Railway will detect your `docker-compose.yml`. For manual setup:

1. Click **+ Add service**
2. Select **PostgreSQL**
3. Select **PostgreSQL** → **Deploy**
4. Link to your application

Repeat for Redis:
1. **+ Add service**
2. **Redis**
3. **Deploy**

#### 4. Configure Environment Variables

1. Go to your **App Service** settings
2. Click **Variables**
3. Add variables from `.env.backend.example`:

```bash
DATABASE_URL=postgresql://...  # Railway provides this
REDIS_URL=redis://...           # Railway provides this
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
... (others from template)
```

#### 5. Configure Deployment

1. Go to **Deployments**
2. Choose **GitHub** trigger
3. Select branch (e.g., `main`)
4. Enable auto-deploy on push

#### 6. Add Custom Domain (Optional)

1. Go to **Environment** → **Domain**
2. Add custom domain
3. Update DNS records
4. Railway handles SSL automatically

#### 7. View Logs

1. Click **Deployments** → **Latest**
2. View real-time logs
3. Check for errors

### Test Deployment

```bash
# Get your Railway URL
# Visit in browser: https://your-railway-app.up.railway.app/health

# For API
curl https://your-railway-app.up.railway.app/api/weather

# Deploy webhook URL for GitHub Actions
# Settings → Deploy Hooks
# Copy the webhook URL
# Add as PROD_DEPLOY_URL in GitHub Secrets
```

---

## Render (Free Tier Option)

Render has a genuinely free tier with no auto-pause, perfect for testing.

### Pros
- ✅ Truly free tier (no credit card needed)
- ✅ No auto-pause (unlike Heroku)
- ✅ GitHub auto-deploy
- ✅ Built-in PostgreSQL & Redis (free tier available)
- ✅ Good for side projects

### Cons
- ❌ Free tier limited resources
- ❌ Slower cold starts
- ❌ Limited to 0.5 GB RAM

### Setup Steps

#### 1. Create Render Account

1. Visit [render.com](https://render.com)
2. Click **Get Started**
3. Sign up with GitHub
4. Authorize access

#### 2. Create Web Service for Backend

1. Click **+ New**
2. Select **Web Service**
3. Connect GitHub repository
4. Choose branch (`main`)
5. Set runtime: **Docker**

Configure:
- **Name:** `weather-backend`
- **Image URL:** `ghcr.io/yourusername/weather-backend:latest`
- **Port:** `8000`
- **Plan:** Free

Environment Variables:
```bash
DATABASE_URL=postgresql://render:password@localhost:5432/weather
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret
...
```

#### 3. Create Web Service for Frontend

Repeat for frontend:
- **Name:** `weather-frontend`
- **Image URL:** `ghcr.io/yourusername/weather-frontend:latest`
- **Port:** `3000`
- **Plan:** Free

#### 4. Add PostgreSQL Database

1. Click **+ New**
2. Select **PostgreSQL**
3. Choose:
   - **Name:** `weather-db`
   - **Database:** `weather`
   - **User:** `render`
   - **Plan:** Free
4. Note the connection string
5. Add to backend environment variables as `DATABASE_URL`

#### 5. Add Redis

1. Click **+ New**
2. Select **Redis**
3. Choose:
   - **Name:** `weather-cache`
   - **Plan:** Free
4. Note the connection URL
5. Add to backend as `REDIS_URL`

#### 6. Configure Auto-Deploy

1. Go to each service
2. **Settings** → **Deploy Hooks**
3. Check **GitHub**
4. Authenticate if needed
5. Select branch to auto-deploy

#### 7. Set Deploy Hook for GitHub Actions

1. Service → **Settings** → **Deploy Hooks**
2. Click **Create Webhook**
3. Copy the webhook URL
4. Add to GitHub Secrets as `PROD_DEPLOY_URL`

### Test Deployment

```bash
# Get your Render URLs (from dashboard)
curl https://weather-backend.onrender.com/health
curl https://weather-frontend.onrender.com/health
```

---

## Fly.io (Good Alternative)

Fly.io offers global deployment with generous free tier.

### Pros
- ✅ Free tier with 3 shared-cpu-1x 256MB VMs
- ✅ Global deployment (closest to user)
- ✅ Simple deployment model
- ✅ Automatic SSL
- ✅ Good documentation

### Cons
- ❌ CLI-based (not web UI driven)
- ❌ More setup required for databases
- ❌ Less automation than Railway/Render

### Quick Setup

```bash
# 1. Install Flyctl
curl -L https://fly.io/install.sh | sh

# 2. Sign up
flyctl auth signup

# 3. Create app
cd backend
flyctl launch
# Respond to prompts, select Postgres addon

# 4. Deploy
flyctl deploy

# 5. Check status
flyctl status

# 6. View logs
flyctl logs
```

### Docker Compose for Fly

Create `fly.toml`:

```toml
app = "weather-backend"
primary_region = "ord"  # Chicago (close to US)

[[services]]
internal_port = 8000
protocol = "tcp"
processes = ["app"]

[[services.ports]]
port = 8000

[build]
dockerfile = "backend/Dockerfile"
```

Deploy:
```bash
flyctl deploy
```

---

## DigitalOcean App Platform

For production deployments with more control.

### Setup

1. Create DigitalOcean account
2. Go to **App Platform**
3. Click **Create App**
4. Connect GitHub repository
5. Select Dockerfile to deploy
6. Configure buildpack:

```yaml
name: weather-pipeline
services:
  - name: backend
    github:
      repo: yourusername/weather-pipeline
      branch: main
    docker_filepath: backend/Dockerfile
    envs:
      - key: DATABASE_URL
        scope: RUN_AND_BUILD_TIME
        value: ${db.username}:${db.password}@${db.host}:5432/weather
    health_check:
      http_path: /health

  - name: frontend
    github:
      repo: yourusername/weather-pipeline
      branch: main
    docker_filepath: frontend/Dockerfile

databases:
  - name: db
    engine: PG
    version: "15"
    production: true
```

Cost: $5/month minimum

---

## AWS ECS (Production Grade)

For serious production deployments.

### Architecture

```
GitHub Actions Builds Docker Images
            ↓
      Push to ECR (AWS Container Registry)
            ↓
      ECS Auto-Deploy
            ↓
    Load Balancer (ALB)
      ↙           ↘
  Backend      Frontend
```

### Setup Steps

```bash
# 1. Create ECS cluster
aws ecs create-cluster --cluster-name weather-pipeline

# 2. Create ECR repositories
aws ecr create-repository --repository-name weather-backend
aws ecr create-repository --repository-name weather-frontend

# 3. Push GitHub CI/CD configuration
# Update .github/workflows/deploy.yml with ECR push step

# 4. Configure task definitions
# See AWS documentation for task definition format

# 5. Create services
aws ecs create-service --cluster weather-pipeline \
  --service-name backend \
  --task-definition weather-backend \
  --desired-count 1
```

**Estimated Cost:** $30-50/month (production grade)

---

## GitHub Pages + Backend (Budget Option)

Deploy frontend to GitHub Pages (free) and backend elsewhere.

### Frontend on GitHub Pages

```bash
# Configure in vite.config.ts
export default {
  base: '/weather-pipeline/',
  // ...
}

# Deploy command
npm run build
git add dist/
git commit -m "Deploy static site"
git push
```

Then in VITE config, update API base to:
```
VITE_API_BASE_URL=https://your-backend-domain/api
```

### Backend on Render/Railway

Deploy backend service separately with its own free tier.

---

## Deployment Checklist

Use this checklist for each platform:

### Before Deployment

- [ ] GitHub repository created
- [ ] Docker images build successfully in CI/CD
- [ ] Environment templates prepared
- [ ] GitHub Secrets configured
- [ ] Database service accessible

### During Deployment

- [ ] App deploys without errors
- [ ] Health check endpoints accessible
- [ ] Logs show no critical errors
- [ ] Database connections established
- [ ] Cache service (Redis) connected

### Post Deployment

- [ ] Frontend loads in browser
- [ ] API returns data: `GET /api/health`
- [ ] WebSocket connection works
- [ ] All environment variables working
- [ ] CORS properly configured
- [ ] SSL certificate active

### Performance Check

- [ ] Frontend load time < 3s
- [ ] API response < 200ms
- [ ] No memory leaks in logs
- [ ] Database pool not exhausted

---

## Multi-Environment Setup

### Staging vs Production

**Staging (Test Environment):**
- Free tier instance
- Test new features
- Staging database
- Staging API keys

**Production (Live Environment):**
- Dedicated resources
- Blue-green deployment
- Production database
- Production API keys

### GitHub Workflow

```yaml
on:
  push:
    branches: [main, develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Staging
        if: github.ref == 'refs/heads/develop'
        run: curl ${{ secrets.STAGING_DEPLOY_URL }}
      
      - name: Deploy to Production
        if: github.ref == 'refs/heads/main'
        run: curl ${{ secrets.PROD_DEPLOY_URL }}
```

---

## Monitoring Deployments

### Check Logs

**Railway:**
```bash
railway logs
```

**Render:**
```bash
# Via Dashboard → Service → Logs
```

**Fly.io:**
```bash
flyctl logs
```

**AWS ECS:**
```bash
aws logs tail /ecs/weather-backend --follow
```

### Common Issues

**502 Bad Gateway:**
- Backend not running
- Health check failing
- Port mismatch

**Connection Refused:**
- Database not accessible
- DNS not resolved
- Firewall blocking

**Out of Memory:**
- Image too large
- Memory leak in code
- Instance type too small

---

## Cost Estimation

### Free Tier Options

| Platform | Cost | Resources |
|----------|------|-----------|
| Railway | $5/month credit | 1 Backend + 1 Frontend +DB |
| Render | Free | Shared resources, limited RAM |
| Fly.io | Free | 3 shared VMs |
| GitHub Pages | Free | Frontend only |

### Production Options

| Platform | Cost | Resources | Scalability |
|----------|------|-----------|-------------|
| Railway | $10-50/mo | Dedicated | Good |
| DigitalOcean | $5-20/mo | Shared/Dedicated | Excellent |
| AWS ECS | $20-100/mo | Flexible | Excellent |
| Heroku | $25-50/mo | Dynos | Good |

---

## Migration Between Platforms

If you need to switch platforms later:

1. **Export Database:**
   ```bash
   pg_dump -h old-host -U user -d database > backup.sql
   ```

2. **Import to New Platform:**
   ```bash
   psql -h new-host -U user -d database < backup.sql
   ```

3. **Update DNS:**
   - Update PROD_DEPLOY_URL in GitHub Secrets
   - Update frontend API URL in environment

4. **Test Before Cutover:**
   - Run full test suite
   - Verify all endpoints
   - Check performance

---

## Recommendation

**For Your Current Setup:**

🟢 **Start with Railway or Render**
- Easiest setup
- Great GitHub integration
- Good free/cheap tier
- Perfect for this project stage

**Graduate to DigitalOcean or AWS when:**
- Needing more resources
- Traffic exceeds free tier
- Requiring custom domain
- Need advanced monitoring

---

## Next Steps

1. **Choose a platform** (Railway recommended)
2. **Create account** and connect GitHub
3. **Deploy backend** service
4. **Deploy frontend** service
5. **Add database** service
6. **Configure environment variables**
7. **Test deployment** with curl/browser
8. **Set GitHub Secrets** with deployment webhook
9. **Test GitHub Actions** trigger deployment
10. **Monitor logs** for issues

---

## Resources

- [Railway Documentation](https://docs.railway.app)
- [Render Documentation](https://render.com/docs)
- [Fly.io Documentation](https://fly.io/docs)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs)
- [DigitalOcean App Platform](https://docs.digitalocean.com/products/app-platform)

---

**Choose your platform and deploy! 🚀**
