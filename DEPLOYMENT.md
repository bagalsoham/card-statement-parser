# Deployment Guide

Complete guide for deploying the Credit Card Statement Parser to production.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Deployment Options](#deployment-options)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Security](#security)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Backend**:
- Python 3.10+
- 2GB RAM (minimum), 4GB RAM (recommended)
- 1 CPU core (minimum), 2+ cores (recommended)
- 10GB disk space

**Frontend**:
- Node.js 16+
- 512MB RAM
- Web server (nginx/Apache)

### External Services

- **Google Gemini API** (for LLM fallback)
- **Domain name** (for production)
- **SSL certificate** (Let's Encrypt recommended)

---

## Environment Setup

### Production Environment Variables

Create `backend/.env.production`:

```bash
# ============================================================================
# PRODUCTION CONFIGURATION
# ============================================================================

# API Keys
GEMINI_API_KEY=your-production-gemini-key

# Server
ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Feature Flags
USE_LLM_FALLBACK=true
CONFIDENCE_THRESHOLD=0.7

# Security
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
MAX_UPLOAD_SIZE=10485760
REQUEST_TIMEOUT=30

# Performance
WORKERS=4
THREADS=2

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
LOGGING_ENDPOINT=https://logs.your-domain.com
```

---

## Deployment Options

### Option 1: Docker (Recommended)

**Pros**:
- Consistent across environments
- Easy scaling
- Simplified dependencies

**Best For**: Most production deployments

### Option 2: Traditional VPS

**Pros**:
- Full control
- Lower cost for small scale

**Best For**: Single server deployments

### Option 3: Cloud Platform (AWS/GCP/Azure)

**Pros**:
- Auto-scaling
- Managed services
- High availability

**Best For**: Enterprise deployments

### Option 4: Platform-as-a-Service (Heroku/Railway)

**Pros**:
- Zero configuration
- Fast deployment

**Best For**: Quick MVP launches

---

## Docker Deployment

### Step 1: Create Dockerfiles

**Backend Dockerfile** (`backend/Dockerfile`):

```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Frontend Dockerfile** (`frontend/Dockerfile`):

```dockerfile
# Build stage
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

### Step 2: Create Docker Compose

**`docker-compose.yml`**:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: cc-parser-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - USE_LLM_FALLBACK=true
      - LOG_LEVEL=INFO
    volumes:
      - ./backend/logs:/app/logs
    networks:
      - cc-parser-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: cc-parser-frontend
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    volumes:
      - ./frontend/nginx/ssl:/etc/nginx/ssl:ro
    networks:
      - cc-parser-network

networks:
  cc-parser-network:
    driver: bridge
```

### Step 3: Deploy

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Step 4: Update Deployment

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Verify deployment
docker-compose ps
docker-compose logs backend
```

---

## Cloud Deployment

### AWS Deployment

#### Architecture

```
┌─────────────┐
│  Route 53   │ (DNS)
└──────┬──────┘
       │
┌──────▼──────┐
│ CloudFront  │ (CDN)
└──────┬──────┘
       │
┌──────▼────────────────────────┐
│  Application Load Balancer    │
└──────┬────────────────────────┘
       │
   ┌───┴───┬────────┐
   │       │        │
┌──▼──┐ ┌──▼──┐ ┌──▼──┐
│ECS  │ │ECS  │ │ECS  │ (Containers)
│Task │ │Task │ │Task │
└─────┘ └─────┘ └─────┘
```

#### Step-by-Step

**1. Create ECR Repository**:
```bash
aws ecr create-repository --repository-name cc-parser-backend
aws ecr create-repository --repository-name cc-parser-frontend
```

**2. Build and Push Images**:
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build
docker build -t cc-parser-backend ./backend
docker build -t cc-parser-frontend ./frontend

# Tag
docker tag cc-parser-backend:latest \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cc-parser-backend:latest

# Push
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cc-parser-backend:latest
```

**3. Create ECS Task Definition**:
```json
{
  "family": "cc-parser-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cc-parser-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "USE_LLM_FALLBACK",
          "value": "true"
        }
      ],
      "secrets": [
        {
          "name": "GEMINI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:gemini-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/cc-parser",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "backend"
        }
      }
    }
  ]
}
```

**4. Create ECS Service**:
```bash
aws ecs create-service \
  --cluster cc-parser-cluster \
  --service-name cc-parser-backend \
  --task-definition cc-parser-backend \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Google Cloud Platform (GCP)

#### Using Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/cc-parser-backend
gcloud run deploy cc-parser-backend \
  --image gcr.io/PROJECT_ID/cc-parser-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars USE_LLM_FALLBACK=true \
  --set-secrets GEMINI_API_KEY=gemini-key:latest
```

### Azure

#### Using Container Instances

```bash
# Create container
az container create \
  --resource-group cc-parser-rg \
  --name cc-parser-backend \
  --image yourregistry.azurecr.io/cc-parser-backend:latest \
  --cpu 1 \
  --memory 2 \
  --registry-login-server yourregistry.azurecr.io \
  --registry-username YOUR_USERNAME \
  --registry-password YOUR_PASSWORD \
  --ports 8000 \
  --environment-variables USE_LLM_FALLBACK=true \
  --secure-environment-variables GEMINI_API_KEY=your-key
```

---

## Traditional VPS Deployment

### Ubuntu 22.04 Server

**1. Initial Setup**:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10
sudo apt install python3.10 python3.10-venv python3-pip -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install nginx
sudo apt install nginx -y

# Install certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

**2. Deploy Backend**:
```bash
# Create app directory
sudo mkdir -p /var/www/cc-parser
sudo chown $USER:$USER /var/www/cc-parser
cd /var/www/cc-parser

# Clone repository
git clone https://github.com/your-username/credit-card-parser.git .

# Setup virtual environment
cd backend
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with production values

# Create systemd service
sudo nano /etc/systemd/system/cc-parser.service
```

**Systemd Service** (`/etc/systemd/system/cc-parser.service`):
```ini
[Unit]
Description=Credit Card Parser API
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/cc-parser/backend
Environment="PATH=/var/www/cc-parser/backend/venv/bin"
ExecStart=/var/www/cc-parser/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**3. Start Backend**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable cc-parser
sudo systemctl start cc-parser
sudo systemctl status cc-parser
```

**4. Deploy Frontend**:
```bash
cd /var/www/cc-parser/frontend
npm install
npm run build

# Copy to nginx
sudo cp -r build/* /var/www/html/
```

**5. Configure Nginx**:
```nginx
# /etc/nginx/sites-available/cc-parser
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Frontend
    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # File upload
        client_max_body_size 10M;
    }

    # WebSocket support (future)
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**6. Enable Site and SSL**:
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/cc-parser /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Setup SSL
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

---

## Security

### 1. Environment Variables

Never commit sensitive data:
```bash
# Add to .gitignore
.env
.env.production
*.key
*.pem
```

### 2. HTTPS Only

Force HTTPS in nginx:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### 3. Rate Limiting

Add to nginx:
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api {
    limit_req zone=api_limit burst=20 nodelay;
    # ... rest of config
}
```

### 4. Firewall Rules

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 5. Secrets Management

Use environment-specific secret managers:

**AWS**: Secrets Manager
```python
import boto3

client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='gemini-api-key')
GEMINI_API_KEY = secret['SecretString']
```

**Docker**: Use secrets
```yaml
services:
  backend:
    secrets:
      - gemini_api_key

secrets:
  gemini_api_key:
    external: true
```

---

## Monitoring

### 1. Health Checks

Add to your monitoring:
```bash
# Cron job to check health
*/5 * * * * curl -f http://localhost:8000/health || systemctl restart cc-parser
```

### 2. Logging

**Centralized Logging** with ELK Stack:
```yaml
# docker-compose.yml
  elasticsearch:
    image: elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
    volumes:
      - es-data:/usr/share/elasticsearch/data

  logstash:
    image: logstash:8.5.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: kibana:8.5.0
    ports:
      - "5601:5601"
```

### 3. Metrics

**Prometheus + Grafana**:
```yaml
# docker-compose.yml
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

### 4. Error Tracking

**Sentry Integration**:
```python
# backend/main.py
import sentry_sdk

sentry_sdk.init(
    dsn=Config.SENTRY_DSN,
    environment="production",
    traces_sample_rate=1.0
)
```

---

## Troubleshooting

### Issue: Container Won't Start

**Solution**:
```bash
# Check logs
docker logs cc-parser-backend

# Check if port is in use
sudo lsof -i :8000

# Restart service
docker-compose restart backend
```

### Issue: High Memory Usage

**Solution**:
```bash
# Reduce workers in uvicorn
CMD ["uvicorn", "main:app", "--workers", "2"]

# Add memory limit
docker run --memory="1g" cc-parser-backend
```

### Issue: Slow Response Times

**Solutions**:
1. Enable caching
2. Increase workers
3. Add load balancer
4. Optimize PDF processing

---

## Rollback Procedure

```bash
# Docker deployment
git checkout <previous-commit>
docker-compose build
docker-compose up -d

# Traditional deployment
sudo systemctl stop cc-parser
cd /var/www/cc-parser
git checkout <previous-commit>
source backend/venv/bin/activate
pip install -r backend/requirements.txt
sudo systemctl start cc-parser
```

---

## Backup & Recovery

### Backup Script

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/cc-parser-$DATE"

mkdir -p $BACKUP_DIR

# Backup configuration
cp /var/www/cc-parser/.env $BACKUP_DIR/

# Backup logs
cp -r /var/www/cc-parser/logs $BACKUP_DIR/

# Create tarball
tar -czf /backups/cc-parser-$DATE.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Upload to S3 (optional)
aws s3 cp /backups/cc-parser-$DATE.tar.gz s3://your-bucket/backups/
```

---

**Last Updated**: 2024-12-17