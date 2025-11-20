# NSE Options Pricer - Docker Deployment Guide

## 🚀 Quick Start

### Local Docker Deployment

```bash
# Build and run the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The application will be available at: **http://localhost:8501**

---

## 📦 VPS Deployment

### Prerequisites

1. VPS with Docker and Docker Compose installed
2. Minimum 1GB RAM, 1 CPU core
3. Port 8501 open (or configure reverse proxy)

### Step 1: Prepare VPS

```bash
# SSH into your VPS
ssh user@your-vps-ip

# Install Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

### Step 2: Transfer Application

**Option A: Using Git (Recommended)**
```bash
# Clone your repository
git clone https://github.com/yourusername/options-pricer.git
cd options-pricer
```

**Option B: Using SCP**
```bash
# From your local machine
scp -r /Users/mac/projects/options-pricer user@your-vps-ip:/home/user/
```

### Step 3: Deploy

```bash
# Navigate to project directory
cd options-pricer

# Build and start the container
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f options-pricer
```

---

## 🌐 Nginx Reverse Proxy (Production Setup)

### Install Nginx

```bash
sudo apt-get update
sudo apt-get install nginx
```

### Configure Nginx

Create `/etc/nginx/sites-available/options-pricer`:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

### Enable and Start Nginx

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/options-pricer /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

## 🔒 SSL with Let's Encrypt (HTTPS)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
sudo certbot renew --dry-run
```

---

## 📊 Docker Commands Reference

### Container Management

```bash
# Start container
docker compose up -d

# Stop container
docker compose down

# Restart container
docker compose restart

# View logs (live)
docker compose logs -f

# View logs (last 100 lines)
docker compose logs --tail=100

# Execute command in container
docker compose exec options-pricer bash

# Check container health
docker compose ps
```

### Image Management

```bash
# Rebuild image (after code changes)
docker compose build --no-cache

# Pull latest images
docker compose pull

# Remove old images
docker image prune -a
```

### Resource Monitoring

```bash
# View container stats
docker stats nse-options-pricer

# View container resource usage
docker compose top
```

---

## 🔧 Environment Variables

Create a `.env` file in the project root:

```env
# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_THEME_BASE=light

# Application Settings
LOG_LEVEL=INFO
ENABLE_ML=false

# Optional: API Keys (for future features)
# OPENAI_API_KEY=your-key-here
```

Update `docker-compose.yml` to use `.env`:

```yaml
services:
  options-pricer:
    env_file:
      - .env
```

---

## 🔄 Update Deployment

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker compose down
docker compose build --no-cache
docker compose up -d

# Or use one command
docker compose up -d --build
```

---

## 📈 Production Considerations

### 1. Resource Limits

Add to `docker-compose.yml`:

```yaml
services:
  options-pricer:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 2. Persistent Logs

```yaml
volumes:
  - ./logs:/app/logs:rw
```

### 3. Automatic Restarts

```yaml
restart: unless-stopped
```

### 4. Firewall Configuration

```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow SSH (before enabling firewall!)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

---

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
docker compose logs options-pricer

# Check disk space
df -h

# Check if port is already in use
sudo netstat -tulpn | grep 8501
```

### Memory issues

```bash
# Check container memory usage
docker stats nse-options-pricer

# Reduce memory in docker-compose.yml
# or upgrade VPS plan
```

### Permission issues

```bash
# Fix logs directory permissions
sudo chown -R $USER:$USER logs/
chmod -R 755 logs/
```

### Can't access from browser

```bash
# Check if container is running
docker compose ps

# Check if port is accessible
curl http://localhost:8501

# Check firewall
sudo ufw status
```

---

## 📞 Support

For issues or questions:
- Check logs: `docker compose logs -f`
- Restart container: `docker compose restart`
- Rebuild: `docker compose up -d --build`

---

## 🎯 Quick VPS Deployment Script

Save as `deploy.sh`:

```bash
#!/bin/bash

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get install docker-compose-plugin -y

# Clone repository (replace with your repo)
git clone https://github.com/yourusername/options-pricer.git
cd options-pricer

# Start application
docker compose up -d

echo "✅ Deployment complete!"
echo "Access your app at: http://$(curl -s ifconfig.me):8501"
```

Run with:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

**🇰🇪 NSE Options Pricer - Ready for Production! 📈**
