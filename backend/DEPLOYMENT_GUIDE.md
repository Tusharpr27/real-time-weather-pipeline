# Phase 1.9: Backend Deployment & Documentation Guide

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Docker Deployment](#docker-deployment)
3. [Staging Environment](#staging-environment)
4. [Production Deployment](#production-deployment)
5. [Cloud Deployments](#cloud-deployments)
6. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
7. [Operatio runbooks](#operational-runbooks)
8. [Performance Optimization](#performance-optimization)
9. [Security Hardening Checklist](#security-hardening-checklist)
10. [Scaling & Load Testing](#scaling--load-testing)

---

## Local Development Setup

### Prerequisites

- Docker & Docker Compose (20.10+)
- Python 3.12+
- PostgreSQL client tools (optional)
- Redis CLI (optional)
- Locust (for load testing)

### Quick Start with Docker Compose

```bash
# 1. Clone and navigate to project
cd "d:\Real time weather data pipeline system\backend"

# 2. Set up environment
cp .env.docker .env

# Edit .env and set development values:
# APP_ENV=development
# API_PORT=8000
# POSTGRES_PASSWORD=dev_password
# REDIS_PASSWORD=dev_password

# 3. Start all services
docker-compose up --build

# 4. Access services
# API: http://localhost:8000
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
# PostgreSQL: localhost:5432 (psql -h localhost -U weather -d weather_db)
# Redis: localhost:6379 (redis-cli)

# 5. Stop services
docker-compose down

# 6. Clean volumes (reset database)
docker-compose down -v
```

### Manual Setup (Without Docker)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development tools

# 3. Set up database
# Start PostgreSQL manually or use container:
docker run -d \
  --name postgres-dev \
  -e POSTGRES_PASSWORD=dev_password \
  -e POSTGRES_DB=weather_db \
  -p 5432:5432 \
  postgres:15-alpine

# 4. Set up Redis
docker run -d \
  --name redis-dev \
  -p 6379:6379 \
  redis:7-alpine

# 5. Run migrations
python -m alembic upgrade head

# 6. Start application
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 7. Verify health
curl http://localhost:8000/api/health
```

### Development Workflow

```bash
# 1. Run tests
pytest tests/ -v
pytest tests/ -v --cov=app  # With coverage

# 2. Run linting
flake8 app/ tests/
pylint app/ tests/
black app/ tests/  # Check formatting

# 3. Run type checking
mypy app/

# 4. Run security checks
bandit -r app/
safety check

# 5. Generate documentation
python generate_api_docs.py
```

---

## Docker Deployment

### Build Docker Image

```bash
# 1. Build image
docker build -t weather-pipeline:latest .

# 2. Tag for registry
docker tag weather-pipeline:latest myregistry.azurecr.io/weather-pipeline:latest

# 3. Push to registry
docker push myregistry.azurecr.io/weather-pipeline:latest

# 4. Verify image
docker images | grep weather-pipeline
docker run --rm -it weather-pipeline:latest /bin/sh  # Test image
```

### Run Container Locally

```bash
# 1. Create .env file with secrets
echo "POSTGRES_PASSWORD=secure_password" > .env
echo "REDIS_PASSWORD=secure_password" >> .env

# 2. Run container with environment
docker run -d \
  --name weather-app \
  -p 8000:8000 \
  --env-file .env \
  -v logs:/app/logs \
  weather-pipeline:latest

# 3. Check logs
docker logs weather-app
docker logs -f weather-app  # Follow logs

# 4. Execute commands in container
docker exec weather-app ps aux
docker exec weather-app python -c "import app; print(app.__version__)"

# 5. Stop container
docker stop weather-app
docker rm weather-app
```

### Docker Compose Deployment

```bash
# 1. Use provided docker-compose.yml
docker-compose -f docker-compose.yml up -d

# 2. Check service status
docker-compose ps

# 3. View logs
docker-compose logs -f app
docker-compose logs -f postgres
docker-compose logs -f redis

# 4. Execute commands
docker-compose exec app python -m pytest

# 5. Scale services (if using swarm)
docker-compose up -d --scale app=3

# 6. Shut down
docker-compose down
docker-compose down -v  # Remove volumes
```

---

## Staging Environment

### Infrastructure Setup

```bash
# 1. Create staging VPC/Network
# - Use separate network from production
# - Restrict access to team IPs only

# 2. Deploy database
# - PostgreSQL 15 with automated backups
# - Enable SSL connections
# - Set up monitoring alerts

# 3. Deploy Redis cache
# - Redis 7 with AUTH
# - Enable persistence (RDB + AOF)
# - Set maxmemory policy

# 4. Configure load balancer
# - Use staging SSL certificate
# - Health check: /api/health every 30 seconds
# - Timeout: 5 seconds
```

### Staging Deployment Script

```bash
#!/bin/bash
# deploy-staging.sh

set -e

echo "🚀 Deploying to Staging..."

STAGING_REGISTRY="staging.registry.example.com"
APP_IMAGE="${STAGING_REGISTRY}/weather-pipeline:staging-$(git rev-parse --short HEAD)"

# 1. Build image
docker build -t ${APP_IMAGE} .

# 2. Push to staging registry
docker push ${APP_IMAGE}

# 3. Update staging deployment
# Using Kubernetes:
kubectl -n staging set image deployment/weather-app \
  weather-app=${APP_IMAGE}

# Or using Docker Swarm:
# docker service update --image ${APP_IMAGE} weather-app-staging

# 4. Wait for rollout
kubectl -n staging rollout status deployment/weather-app

# 5. Run smoke tests
echo "Running smoke tests..."
./tests/smoke-tests.sh staging

# 6. Monitor for errors (30 seconds)
sleep 30
kubectl -n staging logs -l app=weather-app --tail=100

echo "✅ Staging deployment complete!"
```

### Staging Environment Variables

```bash
# .env.staging
APP_ENV=staging
DEBUG=False
API_PORT=8000

POSTGRES_HOST=postgres-staging.internal
POSTGRES_PORT=5432
POSTGRES_USER=weather
POSTGRES_PASSWORD=${STAGING_DB_PASSWORD}
POSTGRES_DB=weather_staging

REDIS_HOST=redis-staging.internal
REDIS_PORT=6379
REDIS_PASSWORD=${STAGING_REDIS_PASSWORD}

WEATHER_API_KEY=${STAGING_WEATHER_API_KEY}
WEATHER_API_PROVIDER=openweathermap

# Monitoring
MONITORING_ENABLED=True
HEALTH_CHECK_ENABLED=True
ERROR_TRACKING_ENABLED=True
AUDIT_LOGGING_ENABLED=True

# Alerts (less aggressive than prod)
ALERT_EMAIL_ENABLED=True
ALERT_EMAIL_RECIPIENTS=team@example.com
ALERT_WEBHOOK_ENABLED=True

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
ALLOWED_ORIGINS=https://staging.example.com
CORS_ENABLED=True
RATE_LIMIT_ENABLED=True
```

---

## Production Deployment

### Pre-Deployment Checklist

```bash
# ✅ Code Quality
- [ ] All tests passing (pytest)
- [ ] No linting errors (flake8, pylint)
- [ ] Type checking passed (mypy)
- [ ] Security checks passed (bandit, safety)
- [ ] Code review approved
- [ ] All dependencies updated to latest secure versions

# ✅ Documentation
- [ ] API documentation updated
- [ ] README.md updated
- [ ] Deployment guide reviewed
- [ ] Changelog updated
- [ ] Architecture diagram current

# ✅ Testing
- [ ] Unit tests: 90%+ coverage
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Performance baseline established
- [ ] Load test successful (100 concurrent users)

# ✅ Infrastructure
- [ ] SSL/TLS certificate valid (>30 days)
- [ ] DNS configured correctly
- [ ] Database backups configured
- [ ] Monitoring alerts configured
- [ ] Rollback plan documented

# ✅ Security
- [ ] Secrets rotated
- [ ] Security scanning passed
- [ ] API keys secured in vault
- [ ] Database credentials updated
- [ ] CORS policy configured

# ✅ Compliance
- [ ] Data retention policies set
- [ ] Audit logging enabled
- [ ] GDPR compliance verified
- [ ] Backup retention verified
- [ ] Legal review completed
```

### Production Deployment Script

```bash
#!/bin/bash
# deploy-production.sh

set -e

PROD_REGISTRY="registry.example.com"
VERSION=$(git describe --tags --always)
APP_IMAGE="${PROD_REGISTRY}/weather-pipeline:${VERSION}"
BACKUP_IMAGE="${PROD_REGISTRY}/weather-pipeline:latest"

echo "🚀 Deploying Version ${VERSION} to Production..."

# 1. Build and push
docker build -t ${APP_IMAGE} .
docker tag ${APP_IMAGE} ${PROD_REGISTRY}/weather-pipeline:latest
docker push ${APP_IMAGE}

# 2. Create backup
BACKUP_FILE="backup-$(date +%Y%m%d-%H%M%S).tar.gz"
echo "📦 Creating backup: $BACKUP_FILE"
# Backup database:
# pg_dump production_db | gzip > "$BACKUP_FILE"
# Upload to S3 or backup storage

# 3. Blue-Green Deployment (Kubernetes)
echo "🔵 Deploying blue (new version)..."
kubectl set image deployment/weather-app-blue \
  weather-app=${APP_IMAGE} -n production \
  --record

# 4. Wait for deployment
kubectl rollout status deployment/weather-app-blue -n production

# 5. Run smoke tests
echo "✔️  Running smoke tests..."
./tests/smoke-tests.sh production

# 6. Switch traffic (via ingress or service)
echo "🟢 Switching traffic to new version..."
kubectl patch service weather-app-service -n production \
  -p '{"spec":{"selector":{"version":"blue"}}}'

# 7. Monitor (5 minutes)
echo "👁️  Monitoring for 5 minutes..."
for i in {1..5}; do
  echo "Minute $i: Checking metrics..."
  kubectl logs -l app=weather-app -n production --tail=50
  sleep 60
done

# 8. Health check
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://api.example.com/api/health)
if [ $HTTP_CODE -ne 200 ]; then
  echo "❌ Health check failed! Rolling back..."
  # Rollback to previous version
  kubectl patch service weather-app-service -n production \
    -p '{"spec":{"selector":{"version":"green"}}}'
  exit 1
fi

echo "✅ Production deployment complete!"
```

### Production Configuration

```bash
# .env.production (DO NOT COMMIT - use secrets manager)
APP_ENV=production
DEBUG=False
API_PORT=8000

# Database
POSTGRES_HOST=${PROD_DB_HOST}  # From AWS RDS, Azure Database, etc.
POSTGRES_PORT=5432
POSTGRES_USER=weather_prod
POSTGRES_PASSWORD=${PROD_DB_PASSWORD}  # From AWS Secrets Manager
POSTGRES_DB=weather_prod
POSTGRES_SSL_MODE=require

# Redis
REDIS_HOST=${PROD_CACHE_HOST}  # From AWS ElastiCache, Azure Cache, etc.
REDIS_PORT=6379
REDIS_PASSWORD=${PROD_REDIS_PASSWORD}
REDIS_SSL=True

# Weather API
WEATHER_API_KEY=${PROD_WEATHER_API_KEY}
WEATHER_API_PROVIDER=openweathermap

# Monitoring & Observability
MONITORING_ENABLED=True
HEALTH_CHECK_ENABLED=True
ERROR_TRACKING_ENABLED=True
AUDIT_LOGGING_ENABLED=True
PROMETHEUS_ENABLED=True
DATADOG_ENABLED=True

# Alerts (aggressive for production)
ALERT_EMAIL_ENABLED=True
ALERT_EMAIL_RECIPIENTS=alerts@example.com,oncall@example.com
ALERT_WEBHOOK_ENABLED=True
ALERT_SLACK_ENABLED=True
ALERT_PAGERDUTY_ENABLED=True

# Logging
LOG_LEVEL=WARNING  # Production - less verbose
LOG_FORMAT=json
LOG_RETENTION_DAYS=90

# Security
ALLOWED_ORIGINS=https://example.com,https://www.example.com
CORS_ENABLED=True
RATE_LIMIT_ENABLED=True
RATE_LIMIT_GLOBAL=1000/minute
RATE_LIMIT_EXPORT=10/minute
HTTPS_REDIRECT=True

# Performance
CACHE_TTL=3600  # 1 hour
API_TIMEOUT=30  # 30 seconds
MAX_CONNECTIONS=100

# Data Retention
WEATHER_DATA_RETENTION_DAYS=30
ALERT_RETENTION_DAYS=90
AUDIT_LOG_RETENTION_DAYS=365
ERROR_LOG_RETENTION_DAYS=180
```

---

## Cloud Deployments

### AWS Deployment

#### Using ECS (Elastic Container Service)

```bash
# 1. Create ECR repository
aws ecr create-repository --repository-name weather-pipeline
aws ecr get-login-password | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com

# 2. Build and push
docker build -t weather-pipeline:latest .
docker tag weather-pipeline:latest ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/weather-pipeline:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/weather-pipeline:latest

# 3. Create ECS task definition (weather-task.json)
aws ecs register-task-definition --cli-input-json file://weather-task.json

# 4. Create ECS service
aws ecs create-service \
  --cluster weather-cluster \
  --service-name weather-service \
  --task-definition weather-task:1 \
  --desired-count 3 \
  --load-balancers targetGroupArn=arn:aws:...,containerName=weather-app,containerPort=8000

# 5. Scale service
aws ecs update-service \
  --cluster weather-cluster \
  --service weather-service \
  --desired-count 5
```

#### Using EKS (Elastic Kubernetes Service)

```bash
# 1. Create EKS cluster
eksctl create cluster \
  --name weather-prod \
  --region us-east-1 \
  --nodegroup-name weather-nodes \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 10 \
  --node-type t3.medium

# 2. Install Helm (package manager for K8s)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# 3. Deploy using Helm chart
helm repo add weather https://charts.example.com
helm install weather-app weather/weather-pipeline \
  --namespace production \
  --create-namespace \
  --values production-values.yaml

# 4. Scale deployment
kubectl scale deployment weather-app --replicas=5 -n production

# 5. Monitor
kubectl get pods -n production
kubectl logs -l app=weather-app -n production
```

### Azure Deployment

#### Using Azure Container Instances (ACI)

```bash
# 1. Create resource group
az group create --name weather-rg --location eastus

# 2. Push image to Azure Container Registry
az acr create --resource-group weather-rg --name weatherregistry --sku Basic
az acr build --registry weatherregistry --image weather-pipeline:latest .

# 3. Deploy to ACI
az container create \
  --resource-group weather-rg \
  --name weather-app \
  --image weatherregistry.azurecr.io/weather-pipeline:latest \
  --ports 8000 \
  --environment-variables APP_ENV=production API_PORT=8000 \
  --registry-login-server weatherregistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password>

# 4. Scale (multiple instances behind load balancer)
for i in {1..3}; do
  az container create \
    --resource-group weather-rg \
    --name weather-app-$i \
    --image weatherregistry.azurecr.io/weather-pipeline:latest \
    --ports 8000 \
    --registry-login-server weatherregistry.azurecr.io \
    --registry-username <username> \
    --registry-password <password>
done
```

#### Using Azure Kubernetes Service (AKS)

```bash
# 1. Create AKS cluster
az aks create \
  --resource-group weather-rg \
  --name weather-aks \
  --node-count 3 \
  --vm-set-type VirtualMachineScaleSets \
  --load-balancer-sku standard

# 2. Get credentials
az aks get-credentials --resource-group weather-rg --name weather-aks

# 3. Deploy using Helm
helm repo add weather https://charts.example.com
helm install weather-app weather/weather-pipeline \
  --namespace production \
  --create-namespace

# 4. Monitor via Azure Portal or CLI
kubectl get nodes
kubectl get services
kubectl logs -l app=weather-app -n production
```

### Google Cloud Deployment

#### Using Cloud Run

```bash
# 1. Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/weather-pipeline

# 2. Deploy to Cloud Run
gcloud run deploy weather-pipeline \
  --image gcr.io/PROJECT_ID/weather-pipeline \
  --platform managed \
  --region us-central1 \
  --set-env-vars APP_ENV=production \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300

# 3. Scale and configure
gcloud run services update weather-pipeline \
  --max-instances 100 \
  --min-instances 3
```

#### Using GKE (Google Kubernetes Engine)

```bash
# 1. Create GKE cluster
gcloud container clusters create weather-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-1

# 2. Deploy using Helm
helm repo add weather https://charts.example.com
helm install weather-app weather/weather-pipeline \
  --namespace production \
  --create-namespace

# 3. Monitor
kubectl kubectl logs -f deployment/weather-app -n production
```

---

## Monitoring & Troubleshooting

### Health Monitoring

```bash
# Check API health
curl http://localhost:8000/api/health -v

# Check all services
curl http://localhost:8000/api/monitoring/health

# Get performance metrics
curl http://localhost:8000/api/monitoring/metrics/overview

# Get dashboard
curl http://localhost:8000/api/monitoring/dashboard
```

### Common Issues & Solutions

#### 1. Database Connection Failed

```bash
# Problem: "Cannot connect to database"

# Solution:
# 1. Verify database is running
docker-compose ps postgres

# 2. Check connection string in .env
echo $POSTGRES_HOST
echo $POSTGRES_PORT

# 3. Test connection
docker-compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB

# 4. Check logs
docker-compose logs postgres

# 5. Rebuild container
docker-compose down
docker-compose up --build
```

#### 2. Memory Usage Too High

```bash
# Problem: Container memory usage exceeds threshold

# Solution:
# 1. Check current memory usage
docker stats

# 2. Identify memory leaks
python -m memory_profiler benchmark.py

# 3. Adjust resource limits in docker-compose.yml
# Increase limits or reduce data retention

# 4. Clear cache
redis-cli FLUSHDB

# 5. Restart service
docker-compose restart app
```

#### 3. Rate Limiting Issues

```bash
# Problem: "Too Many Requests" (429 errors)

# Solution:
# 1. Check current rate limit status
curl -i http://localhost:8000/api/weather/current/Delhi

# 2. Verify rate limit configuration
grep RATE_LIMIT .env

# 3. Adjust limits if needed
# RATE_LIMIT_GLOBAL=2000/minute  # Increase from 1000
# RATE_LIMIT_EXPORT=20/minute    # Increase from 10

# 4. Clear rate limit cache
redis-cli DEL rate_limit:*

# 5. Restart app
docker-compose restart app
```

#### 4. SSL Certificate Expires Soon

```bash
# Problem: SSL certificate expiration warning

# Solution:
# 1. Check certificate expiration
openssl s_client -connect api.example.com:443 -showcerts | grep -A 2 "Issuer:"

# 2. Renew certificate (Let's Encrypt)
certbot renew --dry-run
certbot renew

# 3. Verify new certificate
openssl s_client -connect api.example.com:443 -showcerts

# 4. Restart load balancer/reverse proxy
docker-compose restart nginx  # or your reverse proxy
```

---

## Operational Runbooks

### Rolling Back a Deployment

```bash
#!/bin/bash
# rollback-deployment.sh

NAMESPACE=${1:-production}
PREVIOUS_VERSION=$(git describe --tags --always HEAD~1)

echo "⚠️  Rolling back to version: $PREVIOUS_VERSION"

# 1. Get previous image
PREVIOUS_IMAGE="registry.example.com/weather-pipeline:${PREVIOUS_VERSION}"

# 2. Start previous version (blue-green)
kubectl set image deployment/weather-app-green \
  weather-app=${PREVIOUS_IMAGE} -n ${NAMESPACE}

# 3. Wait for deployment
kubectl rollout status deployment/weather-app-green -n ${NAMESPACE}

# 4. Switch traffic back
kubectl patch service weather-app-service -n ${NAMESPACE} \
  -p '{"spec":{"selector":{"version":"green"}}}'

echo "✅ Rollback complete"
```

### Database Backup & Restore

```bash
#!/bin/bash
# backup-restoredb.sh

# Backup
pg_dump -h $POSTGRES_HOST -U $POSTGRES_USER $POSTGRES_DB | gzip > backup-$(date +%Y%m%d-%H%M%S).sql.gz

# Upload to S3
aws s3 cp backup-*.sql.gz s3://weather-backups/

# Restore
gunzip < backup-*.sql.gz | psql -h $POSTGRES_HOST -U $POSTGRES_USER $POSTGRES_DB
```

### Database Migration

```bash
#!/bin/bash
# migrate-database.sh

VERSION=${1:-head}

echo "🔄 Running database migrations..."

# Run using Alembic
alembic upgrade $VERSION

echo "✅ Migrations complete"
```

### Scaling Services

```bash
#!/bin/bash
# scale-service.sh

REPLICAS=${1:-5}
NAMESPACE=${2:-production}

echo "📈 Scaling to $REPLICAS replicas..."

kubectl scale deployment weather-app \
  --replicas=$REPLICAS \
  -n $NAMESPACE

kubectl get pods -n $NAMESPACE
```

---

## Performance Optimization

### Database Query Optimization

```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_weather_location_timestamp ON weather_data(location_id, timestamp DESC);
CREATE INDEX idx_alerts_location_created ON alerts(location_id, created_at DESC);
CREATE INDEX idx_audit_logs_resource_id ON audit_logs(resource_id);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM weather_data WHERE location_id = 1 ORDER BY timestamp DESC LIMIT 10;

-- Monitor slow queries
SET log_min_duration_statement = 1000;  -- Log queries >1 second
```

### Cache Strategy

```python
# Cache frequently accessed data
CACHE_STRATEGIES = {
    "/api/weather/current/{location}": ("ttl", 1800),  # 30 minutes
    "/api/weather/history/{location}": ("ttl", 3600),  # 1 hour
    "/api/alerts": ("ttl", 300),  # 5 minutes
}
```

### Load Balancing

```bash
# Nginx configuration for load balancing
upstream weather_app {
    server app1:8000;
    server app2:8000;
    server app3:8000;
    
    # Health check
    check interval=3000 rise=2 fall=5 timeout=1000 type=http;
    check_http_send "GET /api/health HTTP/1.0\r\n\r\n";
    check_http_expect_alive http_2xx;
}

server {
    listen 80;
    server_name api.example.com;
    
    location / {
        proxy_pass http://weather_app;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;
    }
}
```

---

## Security Hardening Checklist

```bash
# ✅ Pre-Deployment Security Review

# [ ] HTTPS/TLS
#     - Certificate valid and not expiring soon
#     - TLS 1.2 or higher enforced
#     - Strong cipher suites configured

# [ ] Authentication & Authorization
#     - API key management in place
#     - RBAC configured
#     - JWT tokens properly validated

# [ ] Data Protection
#     - Database encryption at rest enabled
#     - Encryption in transit (TLS) enforced
#     - Secrets not hardcoded or in version control

# [ ] Network Security
#     - Firewall rules restrictive
#     - VPC security groups configured
#     - Access logs enabled

# [ ] Application Security
#     - Input validation and sanitization
#     - SQL injection prevention
#     - XSS protection enabled
#     - CSRF protection enabled
#     - Security headers configured

# [ ] Infrastructure Security
#     - Non-root user for container
#     - File permissions restrictive
#     - Unnecessary services disabled
#     - Regular patching enabled

# [ ] Compliance & Audit
#     - Audit logging enabled
#     - Data retention policies set
#     - GDPR compliance verified
#     - Regular backups tested
```

---

## Scaling & Load Testing

### Load Testing with Locust

```bash
# 1. Install Locust
pip install locust

# 2. Create load test (benchmark.py already created)

# 3. Run load test
locust -f benchmark.py -u 100 -r 10 -t 10m

# 4. Headless mode for CI/CD
locust -f benchmark.py -u 100 -r 10 -t 5m --headless

# 5. Generate HTML report
locust -f benchmark.py -u 100 --headless -t 5m --csv=results/loadtest --html=results/loadtest.html
```

### Auto-Scaling Configuration

```yaml
# Kubernetes HPA (Horizontal Pod Autoscaler)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: weather-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: weather-app
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Next Steps

1. **Review all documentation**: Ensure deployment guides match your infrastructure
2. **Set up CI/CD**: Automate testing and deployment
3. **Configure monitoring**: Set up Prometheus, Grafana, DataDog, or similar
4. **Plan capacity**: Based on load test results, plan infrastructure
5. **Schedule rollout**: Plan phased deployment to production

---

**Created**: 2024  
**Version**: 1.0  
**Last Updated**: 2024
