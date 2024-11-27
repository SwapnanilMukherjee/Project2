# Collaborative Editor Setup Guide

## Prerequisites

### System Requirements
- Python 3.10 or higher
- Node.js 18 or higher
- PostgreSQL 13 or higher
- Redis 6 or higher
- Git

### Development Tools
- Visual Studio Code (recommended)
- PostgreSQL client
- Redis client

## Project Structure
```
collaborative-editor/
├── backend/
│   ├── config/
│   ├── editor/
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── dev.txt
│   │   └── prod.txt
│   ├── scripts/
│   │   ├── setup_db.sh
│   │   └── reset_db.sh
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── .env.example
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf
└── docker-compose.yml
```

## Backend Setup

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements/dev.txt
```

### 2. Database Setup
```bash
# Start PostgreSQL service
sudo service postgresql start

# Create database
sudo -u postgres psql
postgres=# CREATE DATABASE collab_editor;
postgres=# CREATE USER editor_user WITH PASSWORD 'your_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE collab_editor TO editor_user;
postgres=# \q
```

### 3. Redis Setup
```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis service
sudo service redis-server start
```

### 4. Environment Configuration
```bash
# Copy environment file
cp .env.example .env

# Edit .env file with your configurations
nano .env
```

Required .env configuration:
```plaintext
# Backend/.env
DJANGO_SECRET_KEY=your_secret_key_here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=collab_editor
DB_USER=editor_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379

CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### 5. Initialize Database
```bash
# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 6. Start Backend Server
```bash
# Development server
python manage.py runserver

# For WebSocket support
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

## Frontend Setup

### 1. Package Installation
```bash
# Install dependencies
cd frontend
npm install
npm install -D @tailwindcss/typography tailwindcss-animate
```

### 2. Environment Configuration
```bash
# Copy environment file
cp .env.example .env

# Edit .env file
nano .env
```

Required frontend configuration:
```plaintext
# Frontend/.env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws
```

### 3. Start Frontend Development Server
```bash
npm start
```

## Docker Setup (Recommended for Production)

### 1. Build and Run with Docker Compose
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 2. Docker Environment Configuration
Create a `.env` file in the root directory:
```plaintext
# .env
POSTGRES_DB=collab_editor
POSTGRES_USER=editor_user
POSTGRES_PASSWORD=your_password

REDIS_PASSWORD=your_redis_password

DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your_domain.com

CORS_ALLOWED_ORIGINS=https://your_domain.com
```

## Testing

### Backend Tests
```bash
# Run all tests
python manage.py test

# Run specific test module
python manage.py test editor.tests.test_document

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Frontend Tests
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- src/components/Editor/Editor.test.tsx
```

## Development Tools

### Backend Development Tools
```bash
# Install development dependencies
pip install -r requirements/dev.txt

# Format code
black .

# Lint code
flake8

# Type checking
mypy .
```

### Frontend Development Tools
```bash
# ESLint
npm run lint

# Prettier
npm run format

# Type checking
npm run typescript
```

## Common Issues and Solutions

### Backend Issues

1. Database Connection Error
```bash
# Check PostgreSQL service
sudo service postgresql status

# Restart service if needed
sudo service postgresql restart
```

2. Redis Connection Error
```bash
# Check Redis service
sudo service redis-server status

# Restart service if needed
sudo service redis-server restart
```

3. Migration Issues
```bash
# Reset database
./scripts/reset_db.sh

# Create fresh migrations
python manage.py makemigrations
python manage.py migrate
```

### Frontend Issues

1. Node Module Issues
```bash
# Clear node modules and reinstall
rm -rf node_modules
npm install
```

2. Build Issues
```bash
# Clear cache and rebuild
npm clean-cache
npm run build
```

## Additional Configuration

### nginx Configuration (Production)
```nginx
# /etc/nginx/sites-available/collab-editor
server {
    listen 80;
    server_name your_domain.com;

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### SSL Configuration (Production)
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your_domain.com
```

## Monitoring

### Backend Monitoring
```bash
# Check logs
tail -f backend/logs/django.log

# Monitor Redis
redis-cli monitor

# Monitor PostgreSQL
sudo -u postgres psql
postgres=# SELECT * FROM pg_stat_activity;
```

### Frontend Monitoring
```bash
# Build analysis
npm run build -- --stats
npx webpack-bundle-analyzer build/bundle-stats.json
```

## Production Deployment Checklist

1. Backend
- [ ] Set DEBUG=False
- [ ] Configure secure SECRET_KEY
- [ ] Set up SSL certificates
- [ ] Configure database backup
- [ ] Set up monitoring
- [ ] Configure logging

2. Frontend
- [ ] Build production assets
- [ ] Configure CDN
- [ ] Set up error tracking
- [ ] Enable service worker
- [ ] Configure caching

3. Infrastructure
- [ ] Configure firewalls
- [ ] Set up load balancer
- [ ] Configure backup strategy
- [ ] Set up monitoring alerts
- [ ] Document deployment process