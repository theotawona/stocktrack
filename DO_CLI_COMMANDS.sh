#!/usr/bin/env bash
# StockTrack DigitalOcean CLI Commands

# This file contains useful commands for managing your production deployment
# Most commands require the `doctl` CLI tool to be installed and authenticated

# ============================================================================
# INSTALLATION
# ============================================================================

# Install doctl (DigitalOcean CLI)
# macOS:
#   brew install doctl
# Linux:
#   cd ~
#   wget https://github.com/digitalocean/doctl/releases/download/v1.89.0/doctl-1.89.0-linux-amd64.tar.gz
#   tar xf ~/doctl-1.89.0-linux-amd64.tar.gz
#   sudo mv ~/doctl /usr/local/bin
# Windows: Download from https://github.com/digitalocean/doctl/releases

# Authenticate
# doctl auth init


# ============================================================================
# APP MANAGEMENT
# ============================================================================

# List all apps
doctl apps list

# Get app details
doctl apps get APP_ID --format json | jq

# View live logs
doctl apps logs APP_ID --follow

# View logs from last 2 hours
doctl apps logs APP_ID --since 2h

# Restart app (zero downtime)
doctl apps restart APP_ID

# Deploy latest code (trigger redeploy)
doctl apps create-deployment APP_ID


# ============================================================================
# DOMAIN MANAGEMENT
# ============================================================================

# List all domains
doctl compute domain list

# Get domain details
doctl compute domain get your-domain.com

# Add domain to DigitalOcean
doctl compute domain create your-domain.com --ip-address xxx.xxx.xxx.xxx

# List DNS records for domain
doctl compute domain records list your-domain.com

# Create DNS A record
doctl compute domain records create your-domain.com \
  --record-type A \
  --record-name stocktrack \
  --record-data xxx.xxx.xxx.xxx


# ============================================================================
# BACKUPS & DATA
# ============================================================================

# Download database backup from app
# Note: You may need to use DigitalOcean dashboard for file downloads
# Or use rsync if you set up SSH access

# Manual backup script (runs on your local machine)
# python backup_database.py


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
