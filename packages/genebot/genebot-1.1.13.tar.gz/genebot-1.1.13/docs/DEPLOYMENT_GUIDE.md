# Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Trading Bot Python system across different environments, from local development to production cloud deployments.

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows with WSL2
- **Python**: 3.9 or higher
- **Memory**: Minimum 2GB RAM, 4GB+ recommended for production
- **Storage**: Minimum 10GB free space, SSD recommended
- **Network**: Stable internet connection with low latency to exchanges

### Required Software

```bash
# Python and pip
python3 --version  # Should be 3.9+
pip3 --version

# Git
git --version

# Docker (optional but recommended)
docker --version
docker-compose --version

# Database (choose one)
# PostgreSQL (recommended for production)
psql --version

# Or SQLite (for development/testing)
sqlite3 --version
```

## Quick Start Deployment

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/trading-bot-python.git
cd trading-bot-python

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env  # Add your API keys and configuration
```

### 3. Database Setup

```bash
# For PostgreSQL
createdb trading_bot

# For SQLite (development only)
# Database will be created automatically
```

### 4. Initialize and Run

```bash
# Run database migrations
python scripts/init_db.py

# Start the trading bot
python main.py
```

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f trading-bot

# Stop services
docker-compose down
```

### Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  trading-bot:
    build: .
    container_name: trading-bot
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/trading_bot
      - ENVIRONMENT=production
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    ports:
      - "8000:8000"  # Metrics server
      - "8001:8001"  # Health check
    depends_on:
      - db
      - redis
    networks:
      - trading-network

  db:
    image: postgres:13
    container_name: trading-bot-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=trading_bot
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./deployment/scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - trading-network

  redis:
    image: redis:6-alpine
    container_name: trading-bot-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    networks:
      - trading-network

  prometheus:
    image: prom/prometheus:latest
    container_name: trading-bot-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./deployment/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    networks:
      - trading-network

  grafana:
    image: grafana/grafana:latest
    container_name: trading-bot-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./deployment/grafana:/etc/grafana/provisioning
    networks:
      - trading-network

volumes:
  postgres_data:
  prometheus_data:
  grafana_data:

networks:
  trading-network:
    driver: bridge
```

### Custom Docker Build

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the application
RUN pip install -e .

# Create non-root user
RUN useradd --create-home --shell /bin/bash trading
RUN chown -R trading:trading /app
USER trading

# Expose ports
EXPOSE 8000 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python deployment/scripts/health_check.py

# Start command
CMD ["python", "main.py"]
```

## Cloud Deployment

### AWS Deployment

#### Using AWS ECS

```bash
# Build and push Docker image to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com

docker build -t trading-bot .
docker tag trading-bot:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/trading-bot:latest
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/trading-bot:latest
```

#### ECS Task Definition

```json
{
  "family": "trading-bot",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "trading-bot",
      "image": "123456789012.dkr.ecr.us-west-2.amazonaws.com/trading-bot:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-west-2:123456789012:secret:trading-bot/database-url"
        },
        {
          "name": "BINANCE_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-west-2:123456789012:secret:trading-bot/binance-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/trading-bot",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Terraform Configuration

```hcl
# main.tf
provider "aws" {
  region = "us-west-2"
}

# VPC and Networking
resource "aws_vpc" "trading_bot_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "trading-bot-vpc"
  }
}

resource "aws_subnet" "private_subnet" {
  count             = 2
  vpc_id            = aws_vpc.trading_bot_vpc.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "trading-bot-private-subnet-${count.index + 1}"
  }
}

# RDS Database
resource "aws_db_instance" "trading_bot_db" {
  identifier     = "trading-bot-db"
  engine         = "postgres"
  engine_version = "13.7"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  storage_encrypted     = true

  db_name  = "trading_bot"
  username = "postgres"
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.trading_bot_db_subnet_group.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot = true

  tags = {
    Name = "trading-bot-database"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "trading_bot_cluster" {
  name = "trading-bot"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# ECS Service
resource "aws_ecs_service" "trading_bot_service" {
  name            = "trading-bot"
  cluster         = aws_ecs_cluster.trading_bot_cluster.id
  task_definition = aws_ecs_task_definition.trading_bot_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = aws_subnet.private_subnet[*].id
    security_groups = [aws_security_group.ecs_sg.id]
  }
}
```

### Google Cloud Platform (GCP)

#### Using Cloud Run

```bash
# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/PROJECT_ID/trading-bot
gcloud run deploy trading-bot \
  --image gcr.io/PROJECT_ID/trading-bot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production \
  --memory 2Gi \
  --cpu 1
```

#### Cloud Run Configuration

```yaml
# cloudrun.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: trading-bot
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "1"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 1
      containers:
      - image: gcr.io/PROJECT_ID/trading-bot
        resources:
          limits:
            cpu: "1"
            memory: "2Gi"
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-url
              key: url
```

### Azure Deployment

#### Using Container Instances

```bash
# Create resource group
az group create --name trading-bot-rg --location eastus

# Create container instance
az container create \
  --resource-group trading-bot-rg \
  --name trading-bot \
  --image your-registry/trading-bot:latest \
  --cpu 1 \
  --memory 2 \
  --restart-policy Always \
  --environment-variables ENVIRONMENT=production \
  --secure-environment-variables DATABASE_URL=$DATABASE_URL
```

## Kubernetes Deployment

### Kubernetes Manifests

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: trading-bot

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: trading-bot-config
  namespace: trading-bot
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"

---
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: trading-bot-secrets
  namespace: trading-bot
type: Opaque
data:
  DATABASE_URL: <base64-encoded-database-url>
  BINANCE_API_KEY: <base64-encoded-api-key>
  BINANCE_API_SECRET: <base64-encoded-api-secret>

---
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trading-bot
  namespace: trading-bot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: trading-bot
  template:
    metadata:
      labels:
        app: trading-bot
    spec:
      containers:
      - name: trading-bot
        image: your-registry/trading-bot:latest
        ports:
        - containerPort: 8000
        - containerPort: 8001
        envFrom:
        - configMapRef:
            name: trading-bot-config
        - secretRef:
            name: trading-bot-secrets
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5

---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: trading-bot-service
  namespace: trading-bot
spec:
  selector:
    app: trading-bot
  ports:
  - name: metrics
    port: 8000
    targetPort: 8000
  - name: health
    port: 8001
    targetPort: 8001
```

### Helm Chart

```yaml
# helm/trading-bot/Chart.yaml
apiVersion: v2
name: trading-bot
description: A Helm chart for Trading Bot Python
type: application
version: 0.1.0
appVersion: "1.0.0"

# helm/trading-bot/values.yaml
replicaCount: 1

image:
  repository: your-registry/trading-bot
  pullPolicy: IfNotPresent
  tag: "latest"

service:
  type: ClusterIP
  metricsPort: 8000
  healthPort: 8001

ingress:
  enabled: false

resources:
  limits:
    cpu: 1
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi

config:
  environment: production
  logLevel: INFO

secrets:
  databaseUrl: ""
  binanceApiKey: ""
  binanceApiSecret: ""
```

## Environment-Specific Configurations

### Development Environment

```bash
# .env.development
ENVIRONMENT=development
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///trading_bot_dev.db

# Exchange settings (use sandbox/testnet)
BINANCE_SANDBOX=true
COINBASE_SANDBOX=true

# Disable monitoring in development
MONITORING_ENABLED=false
ALERTING_ENABLED=false
```

### Staging Environment

```bash
# .env.staging
ENVIRONMENT=staging
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@staging-db:5432/trading_bot

# Use testnet but with production-like settings
BINANCE_SANDBOX=true
COINBASE_SANDBOX=true

# Enable monitoring but limit alerts
MONITORING_ENABLED=true
ALERTING_ENABLED=true
ALERT_CHANNELS=slack
```

### Production Environment

```bash
# .env.production
ENVIRONMENT=production
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@prod-db:5432/trading_bot

# Live trading
BINANCE_SANDBOX=false
COINBASE_SANDBOX=false

# Full monitoring and alerting
MONITORING_ENABLED=true
ALERTING_ENABLED=true
ALERT_CHANNELS=email,slack,pagerduty
```

## Monitoring and Observability

### Health Checks

```python
# deployment/scripts/health_check.py
#!/usr/bin/env python3
import requests
import sys
import os

def check_health():
    try:
        health_port = os.getenv('HEALTH_PORT', '8001')
        response = requests.get(f'http://localhost:{health_port}/health', timeout=5)
        
        if response.status_code == 200:
            health_data = response.json()
            if health_data.get('status') == 'healthy':
                print("Health check passed")
                return 0
            else:
                print(f"Health check failed: {health_data}")
                return 1
        else:
            print(f"Health check failed with status code: {response.status_code}")
            return 1
            
    except Exception as e:
        print(f"Health check failed with exception: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(check_health())
```

### Logging Configuration

```yaml
# deployment/logging-config.yaml
version: 1
disable_existing_loggers: false

formatters:
  json:
    format: '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}'
  
handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: json
    stream: ext://sys.stdout
  
  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: json
    filename: /app/logs/trading_bot.log
    maxBytes: 52428800  # 50MB
    backupCount: 10

loggers:
  "":
    level: INFO
    handlers: [console, file]
    propagate: false
```

## Security Considerations

### API Key Management

```bash
# Use environment variables or secret management systems
export BINANCE_API_KEY="your-api-key"
export BINANCE_API_SECRET="your-api-secret"

# Or use AWS Secrets Manager
aws secretsmanager create-secret \
  --name "trading-bot/binance-credentials" \
  --description "Binance API credentials for trading bot" \
  --secret-string '{"api_key":"your-key","api_secret":"your-secret"}'
```

### Network Security

```bash
# Firewall rules (UFW example)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8000/tcp  # Metrics (restrict to monitoring network)
sudo ufw allow 8001/tcp  # Health checks (restrict to load balancer)
sudo ufw deny 5432/tcp   # Database (should only be accessible internally)
sudo ufw enable
```

### SSL/TLS Configuration

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name trading-bot.yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/trading-bot.crt;
    ssl_certificate_key /etc/ssl/private/trading-bot.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /health {
        proxy_pass http://localhost:8001;
        access_log off;
    }
}
```

## Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# deployment/scripts/backup_db.sh

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="trading_bot"

# Create backup
pg_dump $DATABASE_URL > "$BACKUP_DIR/trading_bot_$TIMESTAMP.sql"

# Compress backup
gzip "$BACKUP_DIR/trading_bot_$TIMESTAMP.sql"

# Remove backups older than 30 days
find $BACKUP_DIR -name "trading_bot_*.sql.gz" -mtime +30 -delete

echo "Backup completed: trading_bot_$TIMESTAMP.sql.gz"
```

### Automated Backup with Cron

```bash
# Add to crontab
0 2 * * * /app/deployment/scripts/backup_db.sh >> /var/log/backup.log 2>&1
```

## Troubleshooting

### Common Issues

1. **Container Won't Start**
   ```bash
   # Check logs
   docker logs trading-bot
   
   # Check resource usage
   docker stats trading-bot
   
   # Verify configuration
   docker exec trading-bot python -c "from config.manager import ConfigManager; ConfigManager().validate()"
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connectivity
   docker exec trading-bot python -c "
   import psycopg2
   conn = psycopg2.connect('$DATABASE_URL')
   print('Database connection successful')
   "
   ```

3. **Exchange API Issues**
   ```bash
   # Test exchange connectivity
   docker exec trading-bot python -c "
   from src.exchanges.ccxt_adapter import CCXTAdapter
   adapter = CCXTAdapter('binance', {'apiKey': '$BINANCE_API_KEY', 'secret': '$BINANCE_API_SECRET'})
   print('Exchange connection:', adapter.connect())
   "
   ```

### Performance Monitoring

```bash
# Monitor system resources
htop
iotop
nethogs

# Monitor application metrics
curl http://localhost:8000/metrics

# Check application logs
tail -f logs/trading_bot.log | jq '.'
```

This deployment guide provides comprehensive instructions for deploying the Trading Bot Python system across various environments and platforms. Always test deployments in staging environments before production deployment.