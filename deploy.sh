#!/bin/bash

# NSE Options Pricer - Quick Deploy Script for VPS
# Usage: ./deploy.sh

set -e

echo "🚀 Starting NSE Options Pricer Deployment..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${BLUE}📦 Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker installed${NC}"
else
    echo -e "${GREEN}✅ Docker already installed${NC}"
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    echo -e "${BLUE}📦 Installing Docker Compose...${NC}"
    sudo apt-get update
    sudo apt-get install -y docker-compose-plugin
    echo -e "${GREEN}✅ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✅ Docker Compose already installed${NC}"
fi

# Build and start the application
echo -e "${BLUE}🔨 Building and starting application...${NC}"
docker compose down 2>/dev/null || true
docker compose build --no-cache
docker compose up -d

# Wait for application to start
echo -e "${BLUE}⏳ Waiting for application to start...${NC}"
sleep 10

# Check if container is running
if docker compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Application is running!${NC}"
    
    # Get public IP
    PUBLIC_IP=$(curl -s ifconfig.me || echo "localhost")
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}🎉 Deployment Successful!${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "📊 Access your application at:"
    echo -e "   ${BLUE}http://${PUBLIC_IP}:8501${NC}"
    echo ""
    echo -e "📋 Useful commands:"
    echo "   View logs:    docker compose logs -f"
    echo "   Stop app:     docker compose down"
    echo "   Restart app:  docker compose restart"
    echo "   Update app:   git pull && docker compose up -d --build"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo -e "${RED}❌ Deployment failed. Check logs:${NC}"
    docker compose logs
    exit 1
fi
