# SSL/TLS Configuration Guide

Set up HTTPS for your production Weather Data Pipeline deployment.

---

## Why SSL/TLS is Critical

**Security Benefits:**
- 🔒 Encrypts data in transit (passwords, API tokens)
- ✅ Authenticates server identity
- 📈 Improves SEO ranking (HTTPS required)
- 🔐 Enables secure WebSocket (WSS)
- 🛡️ Protects against man-in-the-middle attacks

**Required for:**
- Real-time WebSocket connections
- User authentication
- API calls with credentials
- Production deployments

---

## Automatic SSL (Recommended)

Most cloud platforms handle SSL automatically. Verify:

### Railway.app
- ✅ Automatic SSL included
- ✅ HTTPS by default
- ✅ Auto-renewal
- No setup required

### Render.com
- ✅ SSL included on free tier
- ✅ Auto-generated certificates
- ✅ HSTS enabled
- No setup required

### Fly.io
- ✅ Automatic Let's Encrypt
- ✅ Auto-renewal
- Just deploy, SSL works

### Vercel (Frontend)
- ✅ SSL by default
- ✅ CDN with TLS
- No setup required

**If using these platforms: SKIP to "Configuration" section, SSL is handled for you.**

---

## Manual SSL Setup

### Option 1: Let's Encrypt with Certbot (Recommended)

Best for self-hosted servers.

#### Prerequisites
- Domain name pointing to your server
- Ubuntu/Debian server
- Nginx running

#### 1.1 Install Certbot

```bash
# Install
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Verify
certbot --version
```

#### 1.2 Generate Certificate

```bash
# Generate and auto-configure Nginx
sudo certbot certonly --webroot -w /usr/share/nginx/html \
  -d yourdomain.com \
  -d api.yourdomain.com \
  --email admin@yourdomain.com \
  --agree-tos \
  --non-interactive

# Output shows:
# Successfully received certificate.
# Certificate is saved at: /etc/letsencrypt/live/yourdomain.com/
```

#### 1.3 Configure Nginx for HTTPS

In `nginx/conf.d/default.conf`, uncomment and update the HTTPS section:

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com api.yourdomain.com *.yourdomain.com;
    
    location /.well-known/acme-challenge {
        root /usr/share/nginx/html;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name yourdomain.com api.yourdomain.com *.yourdomain.com;

    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS Header (force HTTPS)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Your existing server configuration
    # /api proxy
    # /ws proxy
    # etc...
}
```

#### 1.4 Test Nginx Configuration

```bash
# Check syntax
sudo nginx -t
# Should output: ok

# Reload Nginx
sudo systemctl reload nginx
```

#### 1.5 Verify HTTPS Works

```bash
# Test domain
curl https://yourdomain.com/health
curl https://api.yourdomain.com/health

# Should return without SSL errors
```

#### 1.6 Auto-Renewal Setup

```bash
# Test auto-renewal (dry run)
sudo certbot renew --dry-run

# Should show:
# The following certificates are not due for renewal yet...
# Congratulations, all renewals succeeded...

# Enable auto-renewal timer
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Check status
sudo systemctl status certbot.timer
```

---

### Option 2: AWS Certificate Manager

For AWS deployments.

#### 2.1 Request Certificate

```bash
# Via AWS CLI
aws acm request-certificate \
  --domain-name yourdomain.com \
  --subject-alternative-names api.yourdomain.com \
  --validation-method DNS \
  --region us-east-1
```

#### 2.2 Validate Domain

1. Go to AWS Console → Certificate Manager
2. Click certificate
3. See validation CNAME records
4. Add CNAME records to your DNS provider

#### 2.3 Connect to Load Balancer

```bash
# Attach certificate to ALB
aws elbv2 modify-listener \
  --listener-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:...
```

---

### Option 3: Self-Signed Certificate (Testing Only)

⚠️ **NOT for production - browsers will warn users**

For testing HTTPS locally:

```bash
# Generate self-signed cert
openssl req -x509 \
  -newkey rsa:4096 \
  -keyout server.key \
  -out server.crt \
  -days 365 \
  -nodes

# Use in Nginx
ssl_certificate /path/to/server.crt;
ssl_certificate_key /path/to/server.key;
```

---

## Nginx SSL Configuration

### Recommended SSL Settings

In `nginx/conf.d/default.conf`:

```nginx
# Modern Configuration (2024)
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:...;
ssl_prefer_server_ciphers off;

# Session settings
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_session_tickets off;

# HSTS (force HTTPS for 1 year)
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# CSP (Content Security Policy)
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
```

### Nginx SSL_STAPLING (OCSP)

Improves SSL performance:

```nginx
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
```

---

## Docker with SSL

### For Docker Compose

Mount certificates:

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/conf.d:/etc/nginx/conf.d
      - /etc/letsencrypt/live/yourdomain.com:/etc/nginx/certs:ro
    environment:
      - NGINX_HOST=yourdomain.com
      - NGINX_PORT=443
```

### Build Docker Image with Certificate

```dockerfile
FROM nginx:alpine
COPY nginx/conf.d /etc/nginx/conf.d
COPY certs/fullchain.pem /etc/nginx/certs/fullchain.pem
COPY certs/privkey.pem /etc/nginx/certs/privkey.pem
EXPOSE 443
CMD ["nginx", "-g", "daemon off;"]
```

---

## WebSocket Secure Connection (WSS)

For real-time updates over HTTPS.

### Nginx WSS Configuration

```nginx
# WebSocket over SSL
location /ws {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # WSS timeouts
    proxy_read_timeout 3600s;
    proxy_send_timeout 3600s;
}
```

### Frontend WebSocket URL

Update `.env.frontend`:

```bash
# Use wss:// for secure WebSocket
VITE_WEBSOCKET_URL=wss://api.yourdomain.com/ws

# Not ws:// (unencrypted)
```

---

## Test SSL Configuration

### Command Line Tools

```bash
# Test SSL/TLS
openssl s_client -connect yourdomain.com:443

# Check certificate validity
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/cert.pem -text -noout

# Test configuration
nmap --script ssl-enum-ciphers -p 443 yourdomain.com

# Get grade from SSL Labs
curl "https://api.ssllabs.com/api/v3/analyze?host=yourdomain.com"
```

### Browser Tools

1. Open DevTools (F12)
2. Go to **Security** tab
3. Should see green lock icon
4. Check certificate validity

### Online Tools

- [SSL Labs](https://www.ssllabs.com/ssltest/)
- [Mozilla SSL Configuration](https://ssl-config.mozilla.org/)
- [Let's Encrypt Check](https://check-your-website.server-daten.de/en)

---

## Troubleshooting SSL

### Issue: "Certificate Not Valid"

**Problem:** Certificate path wrong or permissions denied

**Solution:**
```bash
# Check certificate exists
ls -la /etc/letsencrypt/live/yourdomain.com/

# Fix permissions
sudo chmod 644 /etc/letsencrypt/live/yourdomain.com/fullchain.pem

# Reload Nginx
sudo nginx -t && sudo systemctl reload nginx
```

### Issue: "Mixed Content" Error

**Problem:** Loading resources over HTTP on HTTPS page

**Solution:**
1. Check browser console for HTTP resources
2. Update URLs to HTTPS or protocol-relative URLs
3. Add CSP header to allow only HTTPS

```nginx
add_header Content-Security-Policy "upgrade-insecure-requests;" always;
```

### Issue: "SSL Certificate Chain Incomplete"

**Problem:** Missing intermediate certificates

**Solution:**
```bash
# Regenerate with full chain
sudo certbot renew --force-renewal

# Verify chain
openssl s_client -connect yourdomain.com:443 -showcerts
```

### Issue: "Certificate Expired"

**Problem:** Certificate renewal failed

**Solution:**
```bash
# Manual renewal
sudo certbot renew --force-renewal

# Check renewal logs
sudo cat /var/log/letsencrypt/letsencrypt.log

# Enable auto-renewal
sudo systemctl enable certbot.timer
```

### Issue: "HSTS Error: Preload Required"

**Problem:** Domain requires HSTS preload

**Solution:**
1. Submit to HSTS preload list: https://hstspreload.org/
2. Update header:
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

---

## Security Best Practices

### Checklist

- [ ] HTTPS enforced (redirect HTTP → HTTPS)
- [ ] TLS 1.2+ enabled
- [ ] Weak ciphers disabled
- [ ] HSTS header set
- [ ] OCSP stapling enabled
- [ ] Certificate valid and not expired
- [ ] Auto-renewal configured
- [ ] Security headers set
- [ ] CSP configured
- [ ] CAA records configured

### CAA Records

Let DNS control which CAs can issue certificates for your domain:

```bash
# Add to DNS
yourdomain.com CAA 0 issue "letsencrypt.org"

# Example in Route53
Name: yourdomain.com
Type: CAA
Value: 0 issue "letsencrypt.org"
```

### Security Headers

Recommended headers to set:

```nginx
# Prevent clickjacking
add_header X-Frame-Options "SAMEORIGIN" always;

# Prevent MIME sniffing
add_header X-Content-Type-Options "nosniff" always;

# Enable XSS filter
add_header X-XSS-Protection "1; mode=block" always;

# Referrer policy
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Feature policy
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;

# DNS prefetch
add_header X-DNS-Prefetch-Control "on" always;
```

---

## Certificate Lifecycle

### Monthly Maintenance

```bash
# Check certificate expiration
certbot certificates

# Output shows renewal date
#   Expiration Date: 2024-06-15 (MONTH remaining)
```

### Before Expiration

```bash
# Test renewal (60+ days before)
sudo certbot renew --dry-run

# Force renewal if needed
sudo certbot renew --force-renewal

# Reload Nginx
sudo systemctl reload nginx
```

### After Renewal

```bash
# Verify new certificate
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/cert.pem -noout -dates

# Monitor logs
tail -f /var/log/letsencrypt/letsencrypt.log
```

---

## Migration to SSL

### If Starting Without SSL

1. **Install Certificate:** Follow Let's Encrypt steps above
2. **Update Nginx:** Add SSL configuration
3. **Test HTTP:** Verify before redirecting
4. **Enable Redirect:** Add HTTP→HTTPS redirect
5. **Update URLs:** Change backend settings to HTTPS
6. **Test Everything:** Verify all functionality works

### Zero Downtime Migration

```bash
# 1. Generate new certificate (80 keeps working)
sudo certbot certonly --webroot -w /usr/share/nginx/html \
  -d yourdomain.com

# 2. Update Nginx config (test first)
sudo nginx -t

# 3. Reload (no downtime)
sudo systemctl reload nginx

# 4. Verify both HTTP and HTTPS work
curl http://yourdomain.com/health
curl https://yourdomain.com/health

# 5. Enable HTTP→HTTPS redirect
# Add redirect location block
# Test again
# Reload
```

---

## Platform-Specific SSL Settings

### Railway.app

No manual setup needed. Access URLs:
- Frontend: `https://project-xxxx.railroad.app`
- Backend: `https://api-xxxx.railroad.app`

### Render.com

Free tier includes SSL:
- Frontend: `https://yourservice.onrender.com`
- Backend: `https://yourapi.onrender.com`

Custom domains:
1. Add domain in settings
2. Render auto-provisions certificate
3. Add DNS CNAME record
4. Certificate active in ~5 minutes

### Fly.io

Automatic for all deployed apps:
- Access via `https://app-name.fly.dev`
- Custom domain: Add DNS CNAME, auto SSL

### AWS ECS/CloudFront

Use AWS Certificate Manager (ACM):
1. Request certificate in console
2. Validate via DNS
3. Attach to CloudFront distribution
4. Automatic renewal

---

## Performance Impact on SSL

### Minimal Overhead (Already Fast)

- TLS 1.3: ~1ms handshake overhead
- Session resumption: No new handshake
- OCSP stapling: No client request
- Connection pooling: Reuse connections

### Optimization

```nginx
# Enable HTTP/2 (multiplexing)
listen 443 ssl http2;

# Enable SSL session caching
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;

# Disable session tickets (security)
ssl_session_tickets off;

# Enable OCSP stapling
ssl_stapling on;
```

---

## SSL Certificate Renewal Automation

### Let's Encrypt Auto-Renewal

Already enabled:
```bash
# Check timer
sudo systemctl status certbot.timer

# Manual test
sudo certbot renew --dry-run
```

### Custom Renewal Script

```bash
#!/bin/bash
# /usr/local/bin/renew-ssl.sh

LOG_FILE="/var/log/ssl-renew.log"

echo "Renewing SSL certificate..." >> $LOG_FILE
certbot renew --quiet >> $LOG_FILE 2>&1

if [ $? -eq 0 ]
then
    systemctl reload nginx
    echo "Certificate renewed and nginx reloaded" >> $LOG_FILE
else
    echo "Certificate renewal failed" >> $LOG_FILE
    # Send alert email
    echo "SSL renewal failed" | mail -s "Alert" admin@yourdomain.com
fi
```

Add to crontab:
```bash
# Run daily at 2 AM
0 2 * * * /usr/local/bin/renew-ssl.sh
```

---

## Conclusion

SSL/TLS is essential for production deployment:

✅ **Automatic Platforms** (Railway, Render, Fly.io)
- SSL included by default
- No setup required
- **Recommended for most users**

✅ **Let's Encrypt** (Self-hosted)
- Free certificates
- Auto-renewal
- Industry standard

✅ **AWS/Cloud Provider Certificates**
- Managed SSL
- Integrated with CDN
- Best for enterprise

**Your deployment is now secure with HTTPS! 🔒**

---

## Resources

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Certbot Documentation](https://certbot.eff.org/docs/)
- [Mozilla SSL Configuration](https://ssl-config.mozilla.org/)
- [OWASP HTTPS](https://owasp.org/www-community/attacks/HTTPS_Stripping)
- [SSL Labs Best Practices](https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices)

---

**Production deployment with SSL/TLS is now complete! 🚀**
