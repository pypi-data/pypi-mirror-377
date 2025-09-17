# MultiBrain Deployment Guide

This guide covers various deployment options for MultiBrain, from simple local setups to production-ready cloud deployments.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Nginx Configuration](#nginx-configuration)
5. [SSL/TLS Setup](#ssltls-setup)
6. [Environment Variables](#environment-variables)
7. [Performance Optimization](#performance-optimization)
8. [Monitoring & Logging](#monitoring--logging)

## Local Development

### Quick Start

```bash
# Backend
multibrain-api

# Frontend (separate terminal)
cd frontend
npm run dev
```

### Development with Hot Reload

```bash
# Backend with auto-reload
uvicorn multibrain.api.main:app --reload --host 0.0.0.0 --port 8000

# Frontend with HMR
cd frontend
npm run dev -- --host
```

## Docker Deployment

### Dockerfile for Backend

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY pyproject.toml .
COPY src/ ./src/
RUN pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir .

# Copy frontend build
COPY frontend/dist ./static

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "multibrain.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  multibrain:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MULTIBRAIN_ENV=production
      - MULTIBRAIN_CORS_ORIGINS=https://yourdomain.com
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Building and Running

```bash
# Build frontend first
cd frontend
npm run build
cd ..

# Build Docker image
docker build -t multibrain:latest .

# Run with Docker Compose
docker-compose up -d
```

## Cloud Deployment

### AWS EC2 / DigitalOcean Droplet

1. **Provision a server** (Ubuntu 22.04 recommended)
2. **Install dependencies**:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and Node.js
sudo apt install -y python3-pip python3-venv nodejs npm nginx certbot python3-certbot-nginx

# Install PM2 for process management
sudo npm install -g pm2
```

3. **Clone and setup**:

```bash
# Clone repository
git clone https://spacecruft.org/deepcrayon/multibrain
cd multibrain

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -U pip setuptools wheel
pip install .

# Build frontend
cd frontend
npm install
npm run build
cd ..
```

4. **Create PM2 ecosystem file**:

```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'multibrain-api',
    script: 'venv/bin/uvicorn',
    args: 'multibrain.api.main:app --host 0.0.0.0 --port 8000',
    cwd: '/home/ubuntu/multibrain',
    env: {
      MULTIBRAIN_ENV: 'production'
    }
  }]
};
```

5. **Start with PM2**:

```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### Heroku Deployment

1. **Create `Procfile`**:

```
web: uvicorn multibrain.api.main:app --host 0.0.0.0 --port $PORT
```

2. **Create `runtime.txt`**:

```
python-3.11.7
```

3. **Deploy**:

```bash
heroku create your-multibrain-app
heroku buildpacks:add heroku/nodejs
heroku buildpacks:add heroku/python
git push heroku main
```

### Google Cloud Run

1. **Create `cloudbuild.yaml`**:

```yaml
steps:
  # Build frontend
  - name: 'node:18'
    entrypoint: npm
    args: ['install']
    dir: 'frontend'
  
  - name: 'node:18'
    entrypoint: npm
    args: ['run', 'build']
    dir: 'frontend'
  
  # Build container
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/multibrain', '.']
  
  # Push to registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/multibrain']

# Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'multibrain'
      - '--image=gcr.io/$PROJECT_ID/multibrain'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'
```

## Nginx Configuration

### Basic Configuration

```nginx
# /etc/nginx/sites-available/multibrain
server {
    listen 80;
    server_name yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL configuration (managed by Certbot)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Proxy settings
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # SSE specific settings
    location /api/query/stream {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        proxy_set_header Cache-Control 'no-cache';
        proxy_set_header X-Accel-Buffering 'no';
        proxy_buffering off;
        proxy_read_timeout 86400;
    }
}
```

### Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/multibrain /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL/TLS Setup

### Using Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Using Cloudflare

1. Add your domain to Cloudflare
2. Set SSL/TLS mode to "Full (strict)"
3. Enable "Always Use HTTPS"
4. Configure Page Rules for caching

## Environment Variables

### Backend Configuration

```bash
# .env file
MULTIBRAIN_ENV=production
MULTIBRAIN_CORS_ORIGINS=https://yourdomain.com
MULTIBRAIN_LOG_LEVEL=info
MULTIBRAIN_MAX_CONNECTIONS=100
MULTIBRAIN_TIMEOUT=300
```

### Frontend Configuration

```bash
# frontend/.env.production
VITE_API_URL=https://yourdomain.com/api
```

## Performance Optimization

### 1. Enable Gzip Compression

Add to Nginx configuration:

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
```

### 2. Configure Caching

```nginx
# Static assets
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. Use CDN for Static Assets

```html
<!-- In index.html -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css">
```

### 4. Database Connection Pooling (if using database)

```python
# In your database config
DATABASE_URL = "postgresql://user:pass@localhost/db"
POOL_SIZE = 20
MAX_OVERFLOW = 40
```

## Monitoring & Logging

### 1. Application Logging

```python
# Configure logging in main.py
import logging
from logging.handlers import RotatingFileHandler

# Create logs directory
os.makedirs("logs", exist_ok=True)

# Configure rotating file handler
file_handler = RotatingFileHandler(
    "logs/multibrain.log",
    maxBytes=10485760,  # 10MB
    backupCount=10
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[file_handler]
)
```

### 2. Health Check Endpoint

```python
# Add to your FastAPI routes
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }
```

### 3. Monitoring with Prometheus

```python
# Install prometheus-fastapi-instrumentator
from prometheus_fastapi_instrumentator import Instrumentator

# Add to main.py
Instrumentator().instrument(app).expose(app)
```

### 4. Error Tracking with Sentry

```python
# Install sentry-sdk
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment="production"
)

app.add_middleware(SentryAsgiMiddleware)
```

## Security Best Practices

1. **Use environment variables** for sensitive configuration
2. **Enable CORS** only for your domain
3. **Implement rate limiting**:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/query/stream")
@limiter.limit("10/minute")
async def stream_query(request: Request):
    # Your endpoint logic
```

4. **Regular security updates**:

```bash
# Check for vulnerabilities
pip install safety
safety check

# Update dependencies
pip install -U pip setuptools
pip install -U -r requirements.txt
```

## Troubleshooting

### Common Issues

1. **SSE not working**: Check Nginx buffering settings
2. **CORS errors**: Verify CORS_ORIGINS environment variable
3. **502 Bad Gateway**: Ensure backend is running and accessible
4. **Memory issues**: Adjust worker processes and connection limits

### Debug Commands

```bash
# Check service status
pm2 status
pm2 logs multibrain-api

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Test backend directly
curl http://localhost:8000/health

# Monitor system resources
htop
```

## Backup and Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /home/ubuntu/multibrain/logs/

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /home/ubuntu/multibrain/.env

# Keep only last 7 days of backups
find $BACKUP_DIR -type f -mtime +7 -delete
```

Add to crontab:
```bash
0 2 * * * /home/ubuntu/backup.sh
```

---

For additional support or questions, please refer to the main documentation or open an issue on the repository.