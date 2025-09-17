# Deployment Guide

This guide covers deploying Flet-Easy applications to various platforms and environments, from development to production.

## Overview

Flet-Easy applications can be deployed as:

- **Web Applications**: Browser-based apps
- **Desktop Applications**: Native desktop apps
- **Mobile Applications**: iOS and Android apps
- **Progressive Web Apps (PWA)**: Installable web apps
- **Server Applications**: Multi-user web services

## Web Deployment

### Local Development Server

```python
import flet as ft
import flet_easy as fs

app = fs.FletEasy()

if __name__ == "__main__":
    app.run(
        view=ft.AppView.WEB_BROWSER,
        host="localhost",
        port=8000,
        web_renderer=ft.WebRenderer.HTML  # or ft.WebRenderer.CANVAS_KIT
    )
```

### Production Web Server

```python
import flet as ft
import flet_easy as fs
import os

app = fs.FletEasy()

if __name__ == "__main__":
    app.run(
        view=ft.AppView.WEB_BROWSER,
        host="0.0.0.0",  # Allow external connections
        port=int(os.environ.get("PORT", 8080)),
        web_renderer=ft.WebRenderer.HTML,
        assets_dir="assets",  # Static assets directory
        upload_dir="uploads"  # File upload directory
    )
```

### Docker Deployment

**Dockerfile:**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Run application
CMD ["python", "main.py"]
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  flet-app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
      - HOST=0.0.0.0
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: fletapp
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - flet-app
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
```

### Cloud Platform Deployment

#### Heroku

**Procfile:**

```
web: python main.py
```

**runtime.txt:**

```
python-3.9.18
```

**Deploy commands:**

```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create your-flet-app

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set PORT=8080

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Open app
heroku open
```

#### Railway

**railway.toml:**

```toml
[build]
builder = "NIXPACKS"

[deploy]
healthcheckPath = "/"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

#### Render

**render.yaml:**

```yaml
services:
  - type: web
    name: flet-easy-app
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python main.py"
    envVars:
      - key: PORT
        value: 10000
      - key: SECRET_KEY
        generateValue: true
```

#### Google Cloud Run

**cloudbuild.yaml:**

```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/flet-app', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/flet-app']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'flet-app'
      - '--image'
      - 'gcr.io/$PROJECT_ID/flet-app'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
```

## Desktop Application Deployment

### Packaging with PyInstaller

**build_desktop.py:**

```python
import PyInstaller.__main__
import sys
import os

# Build configuration
PyInstaller.__main__.run([
    'main.py',
    '--name=MyFletApp',
    '--onefile',
    '--windowed',  # No console window
    '--add-data=assets;assets',  # Include assets
    '--icon=assets/icon.ico',  # App icon
    '--distpath=dist',
    '--workpath=build',
    '--specpath=build',
    '--clean',
    '--noconfirm'
])
```

**Build script:**

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
python build_desktop.py

# The executable will be in dist/MyFletApp.exe
```

### Cross-Platform Building

**GitHub Actions workflow (.github/workflows/build.yml):**

```yaml
name: Build Desktop Apps

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller

    - name: Build executable
      run: python build_desktop.py

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: ${{ matrix.os }}-executable
        path: dist/
```

## Mobile Application Deployment

### Building for Mobile

```python
import flet as ft
import flet_easy as fs

app = fs.FletEasy()

# Configure for mobile
@app.page("/")
def mobile_page(data: fs.Datasy):
    return ft.View(
        "/",
        controls=[
            ft.Text("Mobile App", size=24),
            # Mobile-optimized UI
        ],
        scroll=ft.ScrollMode.AUTO,
        padding=ft.padding.all(20)
    )

if __name__ == "__main__":
    app.run(
        view=ft.AppView.FLET_APP_WEB,  # Mobile-optimized view
        port=8080
    )
```

### Progressive Web App (PWA)

**manifest.json:**

```json
{
  "name": "My Flet Easy App",
  "short_name": "FletApp",
  "description": "A Flet-Easy application",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#2196f3",
  "icons": [
    {
      "src": "/assets/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/assets/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

**Service Worker (sw.js):**

```javascript
const CACHE_NAME = 'flet-app-v1';
const urlsToCache = [
  '/',
  '/assets/icon-192.png',
  '/assets/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        return response || fetch(event.request);
      }
    )
  );
});
```

## Production Configuration

### Environment Variables

**.env.production:**

```bash
# App Configuration
DEBUG=False
SECRET_KEY=your-production-secret-key
HOST=0.0.0.0
PORT=8080

# Database
DATABASE_URL=postgresql://user:pass@db:5432/proddb

# Redis Cache
REDIS_URL=redis://redis:6379/0

# Security
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ORIGINS=https://yourdomain.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# File Storage
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE=10485760  # 10MB
```

### Production Settings

**config/production.py:**

```python
import os
from pathlib import Path

class ProductionConfig:
    # Security
    SECRET_KEY = os.environ["SECRET_KEY"]
    DEBUG = False
    
    # Server
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 8080))
    
    # Database
    DATABASE_URL = os.environ["DATABASE_URL"]
    
    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE = Path(os.environ.get("LOG_FILE", "/app/logs/app.log"))
    
    # File handling
    UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "/app/uploads"))
    MAX_UPLOAD_SIZE = int(os.environ.get("MAX_UPLOAD_SIZE", 10485760))
    
    # Performance
    ENABLE_COMPRESSION = True
    CACHE_TIMEOUT = 3600  # 1 hour
```

### Nginx Configuration

**nginx.conf:**

```nginx
events {
    worker_connections 1024;
}

http {
    upstream flet_app {
        server flet-app:8080;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # Gzip compression
        gzip on;
        gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

        # Static files
        location /assets/ {
            alias /app/assets/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # API rate limiting
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://flet_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Main application
        location / {
            proxy_pass http://flet_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

## Monitoring and Logging

### Application Logging

```python
import logging
import sys
from pathlib import Path

def setup_logging(log_level="INFO", log_file=None):
    """Configure application logging"""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # File handler (if specified)
    handlers = [console_handler]
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers
    )
    
    return logging.getLogger(__name__)

# Usage in main.py
logger = setup_logging(
    log_level=os.environ.get("LOG_LEVEL", "INFO"),
    log_file=os.environ.get("LOG_FILE")
)

logger.info("Starting Flet-Easy application")
```

### Health Checks

```python
import flet as ft
import flet_easy as fs
from datetime import datetime

app = fs.FletEasy()

@app.page("/health")
def health_check(data: fs.Datasy):
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        # db_status = check_database()
        
        # Check external services
        # api_status = check_external_apis()
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            # "database": db_status,
            # "external_apis": api_status
        }
        
        return ft.View(
            "/health",
            controls=[ft.Text(str(health_data))]
        )
    except Exception as e:
        return ft.View(
            "/health",
            controls=[ft.Text(f"Unhealthy: {str(e)}")]
        )
```

## Security Best Practices

### 1. Environment Variables

```python
import os
from flet_easy import SecretKey

# Never hardcode secrets
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")

app = fs.FletEasy(secret_key=SecretKey(SECRET_KEY))
```

### 2. Input Validation

```python
def validate_input(data: str) -> bool:
    """Validate user input"""
    if not data or len(data) > 1000:
        return False
    
    # Check for malicious patterns
    dangerous_patterns = ['<script', 'javascript:', 'data:']
    for pattern in dangerous_patterns:
        if pattern.lower() in data.lower():
            return False
    
    return True
```

### 3. Rate Limiting

```python
from collections import defaultdict
from time import time

class RateLimiter:
    def __init__(self, max_requests=100, window=3600):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        now = time()
        client_requests = self.requests[client_id]
        
        # Remove old requests
        client_requests[:] = [req_time for req_time in client_requests 
                             if now - req_time < self.window]
        
        # Check limit
        if len(client_requests) >= self.max_requests:
            return False
        
        client_requests.append(now)
        return True
```

## Performance Optimization

### 1. Caching

```python
from functools import lru_cache
import redis

# In-memory caching
@lru_cache(maxsize=128)
def get_expensive_data(key: str):
    # Expensive computation
    return compute_data(key)

# Redis caching
redis_client = redis.Redis.from_url(os.environ.get("REDIS_URL"))

def cache_get(key: str):
    return redis_client.get(key)

def cache_set(key: str, value: str, ttl: int = 3600):
    redis_client.setex(key, ttl, value)
```

### 2. Database Optimization

```python
import asyncio
import asyncpg

class DatabasePool:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None
    
    async def init_pool(self):
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
    
    async def execute_query(self, query: str, *args):
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**

```bash
# Find process using port
lsof -i :8080
# Kill process
kill -9 <PID>
```

2. **Memory Issues**

```python
# Monitor memory usage
import psutil
import gc

def check_memory():
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")
    
    # Force garbage collection
    gc.collect()
```

3. **SSL Certificate Issues**

```bash
# Generate self-signed certificate for development
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

This deployment guide covers the essential aspects of deploying Flet-Easy applications across different environments and platforms. Choose the deployment method that best fits your needs and scale requirements.
