# 🚀 Deployment Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 500MB free disk space
- Instagram account

## Local Deployment (Recommended)

### Option 1: Quick Start

```bash
# 1. Clone/Download project
cd /Users/pl80an/PycharmProjects/ig-extractor

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env  # Edit with your preferences

# 5. Run application
python run.py

# 6. Open browser
# Navigate to: http://localhost:5000
```

### Option 2: Production Setup

**1. System Setup:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y  # Linux
# or brew update on macOS

# Install Python 3.8+
python3 --version  # Verify version

# Install required system packages
sudo apt install python3-pip python3-venv  # Linux
```

**2. Application Setup:**
```bash
# Create application directory
mkdir -p /opt/instagram-organizer
cd /opt/instagram-organizer

# Copy files
cp -r /path/to/ig-extractor/* .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env
```

**3. Environment Configuration (.env):**
```bash
# Flask
SECRET_KEY=your-very-secret-random-key-here-change-this
FLASK_ENV=production

# Database
DATABASE_URL=sqlite:///data/instagram_organizer.db

# Instagram
MAX_POSTS_PER_FETCH=50
FETCH_DELAY_SECONDS=5

# AI (Optional)
AI_PROVIDER=keyword  # or 'openai' or 'local'
# OPENAI_API_KEY=sk-your-key-here

# Media
THUMBNAIL_SIZE=400
```

**4. Initialize Database:**
```bash
python manage_db.py init
```

**5. Create Systemd Service (Linux):**
```bash
sudo nano /etc/systemd/system/instagram-organizer.service
```

```ini
[Unit]
Description=Instagram Saved Posts Organizer
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/opt/instagram-organizer
Environment="PATH=/opt/instagram-organizer/venv/bin"
ExecStart=/opt/instagram-organizer/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**6. Start Service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable instagram-organizer
sudo systemctl start instagram-organizer
sudo systemctl status instagram-organizer
```

**7. Setup Nginx Reverse Proxy (Optional):**
```bash
sudo apt install nginx

sudo nano /etc/nginx/sites-available/instagram-organizer
```

```nginx
server {
    listen 80;
    server_name your-domain.com;  # or localhost

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Static files
    location /static {
        alias /opt/instagram-organizer/app/static;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/instagram-organizer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Docker Deployment

### Option 3: Docker Container

**1. Create Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p data/thumbnails

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "run.py"]
```

**2. Create docker-compose.yml:**
```yaml
version: '3.8'

services:
  instagram-organizer:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./session-*:/app/session-*
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-secret-key-here
    restart: unless-stopped
```

**3. Build and Run:**
```bash
# Build image
docker-compose build

# Run container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Cloud Deployment

### AWS EC2

```bash
# 1. Launch EC2 instance (t2.micro for free tier)
# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Follow "Production Setup" steps above
# 4. Configure security group (allow port 80/443)
# 5. Optional: Setup SSL with Let's Encrypt
```

### Heroku

```bash
# 1. Create Procfile
echo "web: gunicorn run:app" > Procfile

# 2. Add gunicorn to requirements.txt
echo "gunicorn==21.2.0" >> requirements.txt

# 3. Create Heroku app
heroku create instagram-organizer

# 4. Deploy
git push heroku main

# 5. Scale
heroku ps:scale web=1
```

### DigitalOcean Droplet

```bash
# 1. Create droplet (Ubuntu 22.04)
# 2. Follow "Production Setup" steps
# 3. Configure firewall
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| SECRET_KEY | Flask secret key | auto-generated | Yes |
| FLASK_ENV | Environment | development | No |
| DATABASE_URL | Database path | sqlite:///data/... | No |
| INSTAGRAM_USERNAME | Instagram user | - | No* |
| INSTAGRAM_PASSWORD | Instagram pass | - | No* |
| MAX_POSTS_PER_FETCH | Fetch limit | 50 | No |
| FETCH_DELAY_SECONDS | Rate limit delay | 5 | No |
| AI_PROVIDER | AI provider | keyword | No |
| OPENAI_API_KEY | OpenAI key | - | No** |
| THUMBNAIL_SIZE | Thumbnail size | 400 | No |

\* Set via Settings page in UI  
\** Required only if using OpenAI

### Security Best Practices

**1. Change SECRET_KEY:**
```python
# Generate secure key
python -c "import secrets; print(secrets.token_hex(32))"
```

**2. Use HTTPS:**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com
```

**3. Restrict Access:**
```nginx
# Add to nginx config
auth_basic "Restricted Access";
auth_basic_user_file /etc/nginx/.htpasswd;
```

**4. Regular Backups:**
```bash
# Backup script
#!/bin/bash
tar -czf backup-$(date +%Y%m%d).tar.gz \
    data/ \
    session-* \
    .env
```

## Troubleshooting

### Port Already in Use
```bash
# Find process
lsof -i :5000

# Kill process
kill -9 <PID>

# Or change port in run.py
app.run(port=5001)
```

### Permission Denied
```bash
# Fix permissions
chmod +x run.py
chmod -R 755 app/
```

### Database Locked
```bash
# Stop all instances
killall python

# Reset database
rm data/instagram_organizer.db
python manage_db.py init
```

### Out of Memory
```bash
# Increase swap (Linux)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## Monitoring

### Check Status
```bash
# Systemd
sudo systemctl status instagram-organizer

# Docker
docker-compose ps

# Logs
tail -f /var/log/instagram-organizer/app.log
```

### Performance Monitoring
```bash
# Install htop
sudo apt install htop

# Monitor
htop

# Check disk usage
df -h
du -sh data/
```

## Maintenance

### Update Application
```bash
cd /opt/instagram-organizer
git pull  # If using git
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart instagram-organizer
```

### Backup Database
```bash
# Backup
cp data/instagram_organizer.db data/backup_$(date +%Y%m%d).db

# Restore
cp data/backup_20260509.db data/instagram_organizer.db
```

### Clean Thumbnails
```bash
# Remove orphaned thumbnails
python -c "
from app import create_app, db
from app.models import Post
import os

app = create_app()
with app.app_context():
    # Get all thumbnail paths from DB
    db_thumbs = {p.thumbnail_path for p in Post.query.all() if p.thumbnail_path}
    
    # Get all files in thumbnails directory
    thumb_dir = 'data/thumbnails'
    for file in os.listdir(thumb_dir):
        file_path = os.path.join(thumb_dir, file)
        if file_path not in db_thumbs:
            os.remove(file_path)
            print(f'Removed orphaned: {file}')
"
```

## Scaling

### Optimize Database
```bash
python manage_db.py rebuild-fts
sqlite3 data/instagram_organizer.db "VACUUM;"
```

### Use PostgreSQL (Production)
```bash
# Install PostgreSQL
sudo apt install postgresql

# Create database
sudo -u postgres createdb instagram_organizer

# Update .env
DATABASE_URL=postgresql://user:pass@localhost/instagram_organizer

# Install driver
pip install psycopg2-binary
```

### Load Balancing
```nginx
upstream instagram_app {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
}

server {
    location / {
        proxy_pass http://instagram_app;
    }
}
```

## Support

- **Documentation:** See README.md, INSTALLATION.md
- **Issues:** Check logs in terminal
- **Database:** Use `python manage_db.py stats`
- **Reset:** Delete `data/` directory and reinitialize

## License

MIT License - See LICENSE file for details.
