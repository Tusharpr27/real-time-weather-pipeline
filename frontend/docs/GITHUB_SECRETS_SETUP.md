# GitHub Secrets Setup Guide

This guide walks you through configuring GitHub Secrets needed for CI/CD pipelines and deployments.

## Why GitHub Secrets?

GitHub Secrets securely store sensitive information (API keys, tokens, credentials) that CI/CD workflows need without committing them to the repository.

---

## Accessing GitHub Secrets

1. Navigate to your repository on GitHub
2. Click **Settings** (top right)
3. In left sidebar, click **Secrets and variables** → **Actions**
4. You'll see existing secrets and options to add new ones

---

## Required Secrets

### 1. Automatic Secrets (Already Available)

**GITHUB_TOKEN**
- Automatically provided by GitHub Actions
- Scope: Current repository
- Expires: At end of job
- Use: Docker push to ghcr.io

**Benefits:** No manual setup needed!

---

### 2. Deployment Secrets (Manual Setup)

These are used by the deployment workflow to authenticate with your deployment server.

#### DEPLOY_TOKEN

**Purpose:** Authenticates GitHub Actions to your deployment endpoint

**How to Create:**

Option A - Using a Personal Access Token (GitHub):
1. Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens**
2. Click **Generate new token**
3. Set name: `deployment-token`
4. Select scopes: `read:packages`, `write:packages`
5. Click **Generate token**
6. Copy the token

Option B - Using a Custom Token (Recommended):
1. Generate a random secure token:
```bash
openssl rand -hex 32
# Output: a1b2c3d4e5f6... (copy this)
```

**How to Add to GitHub:**
1. Go to repository **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `DEPLOY_TOKEN`
4. Value: Paste your token
5. Click **Add secret**

---

#### STAGING_DEPLOY_URL

**Purpose:** Webhook URL where staging deployments are sent

**How to Create:**

For Railway.app:
```
https://api.railway.app/webhooks/deploy/staging?token=YOUR_RAILWAY_DEPLOY_TOKEN
```

For Render:
```
https://api.render.com/deploy/service?serviceId=srv_xxxxx&key=rnd_xxxxx
```

For Custom Server:
```
https://your-staging-server.com/api/deploy/webhook
```

**How to Add to GitHub:**
1. Go to **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `STAGING_DEPLOY_URL`
4. Value: Paste your complete webhook URL
5. Click **Add secret**

---

#### PROD_DEPLOY_URL

**Purpose:** Webhook URL where production deployments are sent

**How to Create:**

Same format as STAGING_DEPLOY_URL, but pointing to production environment.

**Example (Custom Server):**
```
https://your-prod-server.com/api/deploy/webhook
```

**How to Add to GitHub:**
1. Go to **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `PROD_DEPLOY_URL`
4. Value: Paste your production webhook URL
5. Click **Add secret**

---

### 3. Optional Secrets (Feature-Specific)

These are optional and only needed if using specific services.

#### CODECOV_TOKEN

**Purpose:** Upload coverage reports to Codecov.io

**How to Create:**
1. Sign up at codecov.io
2. Connect your GitHub repository
3. Go to **Settings** → **Repository upload token**
4. Copy the token

**How to Add:**
1. **Secrets and variables** → **Actions**
2. Create secret: `CODECOV_TOKEN`
3. Paste token

#### SENTRY_DSN

**Purpose:** Send errors to Sentry.io

**How to Create:**
1. Sign up at sentry.io
2. Create a new project
3. Go to **Settings** → **Client Keys (DSN)**
4. Copy the DSN URL

**How to Add:**
1. **Secrets and variables** → **Actions**
2. Create secret: `SENTRY_DSN`
3. Paste DSN

---

## Provider-Specific Setup

### Railway.app Deployment

**Prerequisites:**
- Railway.app account
- Project created

**Steps:**

1. **In Railway Dashboard:**
   - Go to your project
   - Click **Settings**
   - Find **Deploy Trigger**
   - Click **Enable**
   - Copy the webhook URL

2. **In GitHub:**
   - Add `PROD_DEPLOY_URL` secret with Railway webhook
   - No additional configuration needed

3. **Test:**
   - Push to main branch
   - Watch GitHub Actions
   - Check Railway deployment logs

---

### Render Deployment

**Prerequisites:**
- Render.com account
- Service created

**Steps:**

1. **In Render Dashboard:**
   - Select your service
   - Go to **Settings** → **Deploy Hooks**
   - Click **Create Deploy Hook**
   - Copy the hook URL

2. **In GitHub:**
   - Add `PROD_DEPLOY_URL` secret with Render hook URL

3. **Test:**
   - Push to main
   - Workflow triggers automatically

---

### Custom Server Deployment

**Prerequisites:**
- VPS or dedicated server with Docker
- Webhook handler script

**Steps:**

1. **Create Webhook Handler:**

Create file on your server: `/opt/deploy/webhook.js`

```javascript
const express = require('express');
const { exec } = require('child_process');
const crypto = require('crypto');

const app = express();
app.use(express.json());

const DEPLOY_TOKEN = process.env.DEPLOY_TOKEN;
const STAGING_DIR = '/var/www/staging';
const PROD_DIR = '/var/www/production';

app.post('/api/deploy/webhook', (req, res) => {
  // Verify token
  const token = req.headers['x-deploy-token'];
  
  if (!token || crypto.timingSafeEqual(token, DEPLOY_TOKEN)) {
    return res.status(401).json({ error: 'Invalid token' });
  }

  const { environment, image_tag } = req.body;
  const targetDir = environment === 'staging' ? STAGING_DIR : PROD_DIR;

  // Deploy
  exec(`
    cd ${targetDir}
    docker pull ${image_tag}
    docker-compose down
    docker-compose up -d
  `, (error, stdout, stderr) => {
    if (error) {
      return res.status(500).json({ error: stderr });
    }
    res.json({ success: true, logs: stdout });
  });
});

app.listen(3001, () => console.log('Deploy webhook running on :3001'));
```

2. **Set Environment Variable:**

```bash
export DEPLOY_TOKEN="your-secure-token-here"
node webhook.js
```

3. **Configure GitHub Secrets:**

```
PROD_DEPLOY_URL = https://your-server.com:3001/api/deploy/webhook
DEPLOY_TOKEN = your-secure-token-here
```

4. **Update Workflow:**

Modify `.github/workflows/deploy.yml` to send token header:

```yaml
- name: Deploy
  env:
    DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
  run: |
    curl -X POST ${{ secrets.PROD_DEPLOY_URL }} \
      -H "X-Deploy-Token: ${{ secrets.DEPLOY_TOKEN }}" \
      -H "Content-Type: application/json" \
      -d '{
        "environment": "production",
        "image_tag": "${{ env.IMAGE_TAG }}"
      }'
```

---

## Managing Secrets

### View Secrets

In **Settings** → **Secrets and variables** → **Actions**, you'll see:
- Secret name
- Last updated
- Date created

✅ **Note:** Secret values are never displayed, only secret names

### Update Secret

1. Click the secret name
2. Click **Update**
3. Enter new value
4. Click **Update secret**

### Delete Secret

1. Click the secret name
2. Click **Delete**
3. Confirm deletion

---

## Secret Naming Conventions

For clarity and consistency:

```yaml
# Deployment secrets
DEPLOY_TOKEN          # Authentication token
STAGING_DEPLOY_URL    # Staging webhook
PROD_DEPLOY_URL       # Production webhook

# Service secrets
CODECOV_TOKEN         # Code coverage
SENTRY_DSN            # Error tracking
DATABASE_PASSWORD     # Database auth

# API keys
WEATHER_API_KEY       # External API
GITHUB_TOKEN          # (automatic)

# AWS/Cloud secrets (if applicable)
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION
```

---

## Security Best Practices

### Do's ✅

1. **Rotate regularly:** Update secrets every 90 days
2. **Use strong tokens:** At least 32 characters, random
3. **Limit scope:** Only give minimum required permissions
4. **Audit access:** Review who has repository access
5. **Use org secrets:** Share across repos securely (GitHub Teams+)
6. **Enable 2FA:** On your GitHub account

### Don'ts ❌

1. **Never commit secrets** to repository
2. **Never log secrets** in workflow output
3. **Never share secrets** in emails/Slack
4. **Never use production secrets** in testing
5. **Never store secrets** locally in `.env` (committed)

---

## Troubleshooting Secrets

### Secret Not Found in Workflow

**Error:**
```
The action with id 'X' cannot reference an inaccessible secret
```

**Solutions:**
- Secret must be defined in same repository
- Check secret name spelling (case-sensitive)
- Verify secret exists in repository settings
- For fork PRs: secrets aren't available (security)

### Secrets Exposed in Logs

**If a secret is accidentally logged:**

1. **Immediately delete it:**
   - Settings → Secrets → Delete

2. **Regenerate on service:**
   - Update API key on external service
   - GitHub will mask old value in logs

3. **Audit access:**
   - Check repository access
   - Review recent deployments

### Permission Denied Errors

**If error deploying with secret:**

```
401 Unauthorized: Invalid credentials
```

**Check:**
- Token hasn't expired
- Token has correct permissions
- Service URL is correct
- Network connectivity

---

## Testing Secrets

### Safe Testing Method

Use a test workflow to verify secrets without deploying:

Create `.github/workflows/test-secrets.yml`:

```yaml
name: Test Secrets
on: workflow_dispatch

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Test deployment URL
        run: |
          echo "PROD_DEPLOY_URL exists: ${{ secrets.PROD_DEPLOY_URL != '' }}"
          echo "DEPLOY_TOKEN exists: ${{ secrets.DEPLOY_TOKEN != '' }}"
          echo "Length: ${#DEPLOY_TOKEN}"
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

Run: **Actions** → **Test Secrets** → **Run workflow**

---

## Template: Complete Secret Configuration

Use this checklist to ensure all required secrets are configured:

```yaml
# Deployment (Required)
- [ ] DEPLOY_TOKEN - Set to random 32+ char string
- [ ] STAGING_DEPLOY_URL - Set to staging webhook URL
- [ ] PROD_DEPLOY_URL - Set to production webhook URL

# Monitoring (Recommended)
- [ ] CODECOV_TOKEN - Set for coverage tracking
- [ ] SENTRY_DSN - Set for error tracking

# Optional (if using these services)
- [ ] AWS_ACCESS_KEY_ID - AWS credentials
- [ ] AWS_SECRET_ACCESS_KEY - AWS credentials
- [ ] DOCKER_USERNAME - Docker Hub (if pushing there)
- [ ] DOCKER_PASSWORD - Docker Hub (if pushing there)

# Verify All Are Set
For each environment (staging/prod):
  - [ ] URL is accessible
  - [ ] Token is valid
  - [ ] Network firewall allows GitHub IPs
  - [ ] Test deployment works
```

---

## Quick Reference

### Secret Access in Workflows

```yaml
# In workflow steps
steps:
  - name: Use secret
    run: |
      echo ${{ secrets.SECRET_NAME }}
    env:
      MY_SECRET: ${{ secrets.SECRET_NAME }}
```

### Common Patterns

**GitHub Container Registry:**
```yaml
docker login -u ${{ github.actor }} -p ${{ secrets.GITHUB_TOKEN }} ghcr.io
docker push ghcr.io/${{ github.repository }}/app:latest
```

**Custom API:**
```yaml
curl -X POST https://api.example.com/deploy \
  -H "Authorization: Bearer ${{ secrets.DEPLOY_TOKEN }}" \
  -d @payload.json
```

---

## Resources

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub Actions Security](https://docs.github.com/en/actions/security-guides)
- [Best Practices Guide](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

---

**All secrets configured? Time to deploy! 🚀**
