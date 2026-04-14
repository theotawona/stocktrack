#!/usr/bin/env bash
# StockTrack — Useful Server Commands
# Run these on your DigitalOcean Droplet via SSH: ssh root@YOUR_DROPLET_IP

# ============================================================================
# APP MANAGEMENT
# ============================================================================

# View live logs
docker compose -f /opt/stocktrack/docker-compose.yml logs -f

# View last 100 log lines
docker compose -f /opt/stocktrack/docker-compose.yml logs --tail 100

# Check app status
docker compose -f /opt/stocktrack/docker-compose.yml ps

# Restart the app
docker compose -f /opt/stocktrack/docker-compose.yml restart

# Stop the app
docker compose -f /opt/stocktrack/docker-compose.yml down

# Start the app
docker compose -f /opt/stocktrack/docker-compose.yml up -d

# Rebuild and restart (after code changes)
cd /opt/stocktrack && git pull origin main && docker compose up -d --build


# ============================================================================
# DEPLOY LATEST CODE (all-in-one)
# ============================================================================

# /opt/stocktrack/deploy.sh
# Or manually:
cd /opt/stocktrack
git pull origin main
docker compose up -d --build


# ============================================================================
# DATABASE & BACKUPS
# ============================================================================

# Run backup manually
/opt/backup-stocktrack.sh

# List backups
ls -lh /opt/stocktrack-backups/

# Find the Docker volume path
docker volume inspect stocktrack_stocktrack-data -f '{{.Mountpoint}}'

# Restore a backup (STOP APP FIRST)
# docker compose -f /opt/stocktrack/docker-compose.yml down
# VOLUME_PATH=$(docker volume inspect stocktrack_stocktrack-data -f '{{.Mountpoint}}')
# cp /opt/stocktrack-backups/stock_tracker_YYYYMMDD_HHMMSS.db "$VOLUME_PATH/stock_tracker.db"
# docker compose -f /opt/stocktrack/docker-compose.yml up -d


# ============================================================================
# NGINX & SSL
# ============================================================================

# Test Nginx config
nginx -t

# Reload Nginx
systemctl reload nginx

# View Nginx error logs
tail -50 /var/log/nginx/error.log

# Check SSL certificate status
certbot certificates

# Renew SSL (normally auto, but can force)
certbot renew

# Test auto-renewal
certbot renew --dry-run


# ============================================================================
# SERVER HEALTH
# ============================================================================

# Check disk usage
df -h

# Check memory usage
free -h

# Check running processes
htop

# Check Docker disk usage
docker system df

# Clean unused Docker images/volumes
docker system prune -a


# ============================================================================
# DOMAIN MANAGEMENT (via doctl CLI, optional)
# ============================================================================

# Install doctl: https://docs.digitalocean.com/reference/doctl/how-to/install/
# doctl auth init

# Add domain
# doctl compute domain create your-domain.com --ip-address YOUR_DROPLET_IP

# Create A record
# doctl compute domain records create your-domain.com \
#   --record-type A --record-name stocktrack --record-data YOUR_DROPLET_IP


# ============================================================================
# MONITORING & TROUBLESHOOTING
# ============================================================================

# View deployment history
doctl apps list-deployments APP_ID

# Get specific deployment details
doctl apps get-deployment APP_ID DEPLOYMENT_ID

# View app metrics (if available)
doctl monitoring metrics list APP_ID


# ============================================================================
# ENVIRONMENT & SECRETS
# ============================================================================

# View environment variables
doctl apps spec get APP_ID | jq '.spec.services[0].envs'

# Update environment variable
# Edit via DigitalOcean dashboard: Apps → Your App → Settings → Env Variables

# Add secret
# 1. Go to DigitalOcean Dashboard
# 2. Apps → Your App → Settings → Component → Add Secret


# ============================================================================
# QUICK DIAGNOSTICS
# ============================================================================

# Check if app is running
curl https://your-custom-domain.com/_stcore/health

# Check DNS resolution
nslookup your-domain.com
# or
dig your-domain.com

# Test Docker image locally before deployment
docker build -t stocktrack .
docker run -p 8501:8501 stocktrack

# Verify app.yaml syntax
cat app.yaml  # Review manually or validate with YAML validator


# ============================================================================
# COST INFORMATION
# ============================================================================

# Get billing information
doctl billing get

# View account balance
doctl account get


# ============================================================================
# USEFUL LINKS
# ============================================================================

# DigitalOcean App Platform Docs:
# https://docs.digitalocean.com/products/app-platform/

# Streamlit Cloud Docs:
# https://docs.streamlit.io/deploy

# Docker Documentation:
# https://docs.docker.com/

# Troubleshooting Guide:
# See DEPLOYMENT_GUIDE.md in your repository


# ============================================================================
# EXAMPLE WORKFLOW: Update Your App
# ============================================================================

# 1. Make changes to your code locally
# 2. Commit and push to GitHub:
#    git add .
#    git commit -m "Update feature X"
#    git push
# 3. Wait ~5 minutes for automatic deployment
# 4. Or manually trigger: doctl apps create-deployment APP_ID


# ============================================================================
# EXAMPLE WORKFLOW: Rollback to Previous Version
# ============================================================================

# 1. View deployment history:
#    doctl apps list-deployments APP_ID
# 2. Find the deployment ID of the version to rollback to
# 3. In DigitalOcean dashboard:
#    Apps → Your App → Deployments → Click deployment → Rollback


# ============================================================================
# SCALING UP (If Performance Issues)
# ============================================================================

# Current instance: basic-xs ($12/month, 0.25 vCPU, 512MB)
# Upgrade options:
#   - basic-s ($18/month, 0.5 vCPU, 1GB)
#   - basic-m ($36/month, 1 vCPU, 2GB)
#
# To upgrade:
# 1. DigitalOcean Dashboard → Apps → Your App → Settings
# 2. Find "Instance Size" section
# 3. Select new size and confirm

# Multiple instances:
# 1. Change "instance_count" in app.yaml
# 2. Commit and push
# 3. DigitalOcean auto-deploys with load balancer


# ============================================================================
# SUPPORT
# ============================================================================

# If you get stuck:
# - Read DEPLOYMENT_GUIDE.md in your repository
# - Check DigitalOcean Support: https://www.digitalocean.com/support
# - View logs: doctl apps logs APP_ID --follow
