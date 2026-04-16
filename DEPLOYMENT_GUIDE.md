# StockTrack Production Deployment Guide

**Deployment Target:** DigitalOcean Droplet  
**Tech Stack:** Docker + Docker Compose + Nginx + Streamlit + SQLite  
**Estimated Cost:** $6/month (Droplet) + custom domain  
**Estimated Setup Time:** 30-45 minutes

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Step 1: Prepare Your GitHub Repository](#step-1-prepare-your-github-repository)
3. [Step 2: Create a DigitalOcean Droplet](#step-2-create-a-digitalocean-droplet)
4. [Step 3: Install Docker on the Droplet](#step-3-install-docker-on-the-droplet)
5. [Step 4: Deploy StockTrack](#step-4-deploy-stocktrack)
6. [Step 5: Set Up Nginx & SSL](#step-5-set-up-nginx--ssl)
7. [Step 6: Configure Custom Domain](#step-6-configure-custom-domain)
8. [Step 7: Set Up Automatic Backups](#step-7-set-up-automatic-backups)
9. [Step 8: Set Up Auto-Deploy from GitHub](#step-8-set-up-auto-deploy-from-github)
10. [Updating the App](#updating-the-app)
11. [Monitoring & Maintenance](#monitoring--maintenance)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- ✅ GitHub account with your repo pushed (you already have `theotawona/stocktrack`)
- ✅ DigitalOcean account (sign up at [digitalocean.com](https://digitalocean.com))
- ✅ Custom domain (optional but recommended)
- ✅ These files in your repo:
  - `Dockerfile` ✓
  - `.dockerignore` ✓
  - `docker-compose.yml` ✓
  - `backup_database.py` ✓

---

## Why a Droplet Instead of App Platform?

StockTrack uses **SQLite** — a file-based database that lives on disk. App Platform runs stateless containers that lose their filesystem on every deploy. A Droplet gives you a **real persistent server** where your database safely stays on disk across deployments and reboots.

| Feature | Droplet | App Platform |
|---------|---------|-------------|
| Cost | **$6/month** | $12/month |
| SQLite persistence | **Native — just works** | Requires workarounds |
| Full server access | **Yes (SSH)** | No |
| Auto-deploy from GitHub | Webhook script | Built-in |
| SSL (HTTPS) | Certbot (free) | Built-in |
| Backups | Cron + volume snapshot | Manual |

---

## Step 1: Prepare Your GitHub Repository

Your repo is already on GitHub at `theotawona/stocktrack`. Make sure the latest code is pushed:

```bash
git add .
git commit -m "Deployment configuration"
git push origin main
```

---

## Step 2: Create a DigitalOcean Droplet

### 2.1 Create Account & Add Payment
1. Go to [digitalocean.com](https://digitalocean.com) and sign up
2. Add a payment method (credit card or PayPal)

### 2.2 Create the Droplet
1. Click **Create → Droplets**
2. Choose these settings:
   - **Region:** Choose the closest to your users (e.g., London, Frankfurt, or Johannesburg-closest)
   - **Image:** **Ubuntu 24.04 LTS**
   - **Size:** **Basic → Regular → $6/month** (1 vCPU, 1 GB RAM, 25 GB SSD)
   - **Authentication:** Choose **SSH Key** (recommended) or Password
   - **Hostname:** `stocktrack`
3. Click **Create Droplet**
4. Note the **IP address** once it's ready (e.g., `164.92.xxx.xxx`)

### 2.3 Set Up SSH Key (if you chose SSH)

If you don't have an SSH key yet:
```powershell
# On your Windows machine (PowerShell):
ssh-keygen -t ed25519 -C "your-email@example.com"
# Press Enter for defaults
# Copy your public key:
Get-Content ~/.ssh/id_ed25519.pub
```
Paste the public key into the DigitalOcean SSH key field when creating the Droplet.

---

## Step 3: Install Docker on the Droplet

### 3.1 SSH into Your Droplet

```bash
ssh root@YOUR_DROPLET_IP
```

### 3.2 Install Docker & Docker Compose

Run these commands on the Droplet:

```bash
# Update system packages
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose plugin
apt install -y docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

### 3.3 Install Nginx & Certbot (for SSL)

```bash
apt install -y nginx certbot python3-certbot-nginx
```

### 3.4 Set Up Firewall

```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
```

> **Note:** We do NOT open port 8501 publicly. Nginx will proxy traffic to it.

---

## Step 4: Deploy StockTrack

### 4.1 Clone Your Repository

```bash
cd /opt
git clone https://github.com/theotawona/stocktrack.git
cd stocktrack
```

### 4.2 Build and Start the App

```bash
docker compose up -d --build
```

This will:
- Build the Docker image from your Dockerfile
- Start StockTrack on port 8501
- Create a persistent Docker volume for your SQLite database at `/app/data/`

### 4.3 Verify It's Running

```bash
docker compose ps
# Should show stocktrack running, healthy

curl http://localhost:8501/app/_stcore/health
# Should return "ok"
```

---

## Step 5: Set Up Nginx & SSL

### 5.1 Create Nginx Configuration

```bash
mkdir -p /var/www/stocktrack-landing
cp /opt/stocktrack/deploy/landing/index.html /var/www/stocktrack-landing/index.html
cp /opt/stocktrack/deploy/nginx/stocktrack.conf /etc/nginx/sites-available/stocktrack
```

This setup gives you:
- A branded landing page at `/` for clean social/link previews
- The Streamlit app at `/app/`

If your domain is not `ca-stocktrack.com`, edit `server_name` in `/etc/nginx/sites-available/stocktrack` before enabling the site.

```nginx
server {
  listen 80;
  listen [::]:80;
  server_name ca-stocktrack.com www.ca-stocktrack.com;

  root /var/www/stocktrack-landing;
  index index.html;

  # Branded home page for clean link previews and browser tab title.
  location = / {
    try_files /index.html =404;
  }

  # Streamlit app runs under /app.
  location /app/ {
    proxy_pass http://127.0.0.1:8501/app/;
    proxy_http_version 1.1;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    proxy_read_timeout 86400;
    proxy_buffering off;
  }

  # ACME challenge path for Certbot.
  location /.well-known/acme-challenge/ {
    root /var/www/certbot;
    try_files $uri =404;
  }

  # Optional direct link path.
  location = /login {
    return 301 /app/;
    }
}
```

### 5.2 Enable the Site

```bash
ln -s /etc/nginx/sites-available/stocktrack /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
nginx -t        # Test config — should say "ok"
systemctl reload nginx
```

### 5.3 Test with HTTP

Visit `http://YOUR_DROPLET_IP` in your browser:
- `/` should show your branded StockTrack landing page
- `/app/` should open the Streamlit app

### 5.4 Add SSL Certificate (after domain is pointing to your IP)

```bash
certbot --nginx -d YOUR_DOMAIN -d www.YOUR_DOMAIN
```

Certbot will:
- Get a free Let's Encrypt SSL certificate
- Automatically configure Nginx for HTTPS
- Set up auto-renewal

**Test auto-renewal:**
```bash
certbot renew --dry-run
```

---

## Step 6: Configure Custom Domain

### 6.1 Point Your Domain to the Droplet

Go to your domain registrar (GoDaddy, Namecheap, etc.) and create:

| Record Type | Name | Value |
|-------------|------|-------|
| **A** | `@` or `stocktrack` | `YOUR_DROPLET_IP` |

Example: If your domain is `stocktrack.globvest.co.za`:
- **A record:** `stocktrack` → `164.92.xxx.xxx`

### 6.2 Wait for DNS Propagation

DNS changes take **15 minutes to 48 hours**. You can check progress:
```bash
nslookup stocktrack.yourdomain.com
```

### 6.3 Update Nginx & Get SSL

Once the domain resolves to your IP:

```bash
# Update the server_name in Nginx config
nano /etc/nginx/sites-available/stocktrack
# Change: server_name YOUR_DOMAIN;  →  server_name stocktrack.yourdomain.com;
systemctl reload nginx

# Get SSL certificate
certbot --nginx -d stocktrack.yourdomain.com
```

---

## Step 7: Set Up Automatic Backups

### 7.1 Create a Backup Script on the Droplet

```bash
mkdir -p /opt/stocktrack-backups

cat > /opt/backup-stocktrack.sh << 'EOF'
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/stocktrack-backups"
VOLUME_PATH=$(docker volume inspect stocktrack_stocktrack-data -f '{{.Mountpoint}}')

# Copy the database from the Docker volume
cp "$VOLUME_PATH/stock_tracker.db" "$BACKUP_DIR/stock_tracker_$TIMESTAMP.db"

# Keep only last 14 days of backups
find "$BACKUP_DIR" -name "*.db" -mtime +14 -delete

echo "Backup complete: stock_tracker_$TIMESTAMP.db"
EOF

chmod +x /opt/backup-stocktrack.sh
```

### 7.2 Schedule Daily Backups with Cron

```bash
crontab -e
```

Add this line (backs up every day at 2 AM):
```
0 2 * * * /opt/backup-stocktrack.sh >> /var/log/stocktrack-backup.log 2>&1
```

### 7.3 Test the Backup

```bash
/opt/backup-stocktrack.sh
ls -la /opt/stocktrack-backups/
```

### 7.4 Optional: Enable DigitalOcean Droplet Backups

For an extra **$1.20/month**, DigitalOcean can snapshot your entire Droplet weekly:
1. Go to your Droplet → **Backups** tab
2. Click **Enable Backups**

This gives you full server recovery — recommended for production.

---

## Step 8: Set Up Auto-Deploy from GitHub

When you push code to GitHub, the Droplet can automatically pull and redeploy.

### 8.1 Create a Deploy Script

```bash
cat > /opt/stocktrack/deploy.sh << 'EOF'
#!/bin/bash
cd /opt/stocktrack

# Pull latest code
git pull origin main

# Rebuild and restart (keeps the database volume intact)
docker compose up -d --build

echo "Deploy complete: $(date)"
EOF

chmod +x /opt/stocktrack/deploy.sh
```

### 8.2 Option A: Manual Deploy (Simplest)

Whenever you push to GitHub, SSH into the Droplet and run:
```bash
/opt/stocktrack/deploy.sh
```

### 8.2 Option B: GitHub Webhook (Automatic)

For automatic deploys, you can set up a lightweight webhook listener. This is optional — manual deploys work fine for a small team.

---

## Updating the App

After pushing changes to GitHub:

```bash
# SSH into your Droplet
ssh root@YOUR_DROPLET_IP

# Run the deploy script
/opt/stocktrack/deploy.sh
```

Or in one command from your local machine:
```bash
ssh root@YOUR_DROPLET_IP "/opt/stocktrack/deploy.sh"
```

Your database is **never affected** by redeployments — it lives in a Docker volume separate from the app code.

---

## Monitoring & Maintenance

### View App Logs
```bash
# Live logs
docker compose -f /opt/stocktrack/docker-compose.yml logs -f

# Last 100 lines
docker compose -f /opt/stocktrack/docker-compose.yml logs --tail 100
```

### Check App Status
```bash
docker compose -f /opt/stocktrack/docker-compose.yml ps
```

### Restart the App
```bash
docker compose -f /opt/stocktrack/docker-compose.yml restart
```

### Check Disk Usage
```bash
df -h           # Overall disk usage
du -sh /opt/stocktrack-backups/  # Backup size
docker system df  # Docker disk usage
```

### Check Server Resources
```bash
htop            # CPU & memory (install: apt install htop)
free -h         # Memory usage
```

---

## Troubleshooting

### App Won't Start
```bash
docker compose logs stocktrack
```
Common causes:
- Port 8501 already in use: `lsof -i :8501`
- Build error: Check `requirements.txt` is correct
- Fix and rebuild: `docker compose up -d --build`

### "502 Bad Gateway" in Browser
Nginx is running but can't reach the app:
```bash
# Check if Docker container is running
docker compose ps

# Check if app is healthy
curl http://localhost:8501/_stcore/health

# Restart if needed
docker compose restart
```

### Database Errors
```
Error: database is locked
```
SQLite allows one writer at a time. For a small team this is rarely an issue. If it persists:
```bash
# Check if multiple containers are running
docker compose ps
# Should show exactly 1 container
```

### SSL Certificate Issues
```bash
# Check certificate status
certbot certificates

# Force renewal
certbot renew --force-renewal

# Check Nginx config
nginx -t
```

### Custom Domain Not Working
- Ensure the A record points to your Droplet's IP
- Check propagation: `nslookup yourdomain.com`
- DNS changes can take up to 48 hours
- After DNS resolves, run `certbot --nginx -d yourdomain.com`

### Running Out of Disk Space
```bash
# Clean old Docker images
docker system prune -a

# Check backup folder size
du -sh /opt/stocktrack-backups/
```

### Need to Restore a Backup
```bash
# Stop the app
docker compose -f /opt/stocktrack/docker-compose.yml down

# Find the volume path
VOLUME_PATH=$(docker volume inspect stocktrack_stocktrack-data -f '{{.Mountpoint}}')

# Copy backup over the current database
cp /opt/stocktrack-backups/stock_tracker_YYYYMMDD_HHMMSS.db "$VOLUME_PATH/stock_tracker.db"

# Start the app
docker compose -f /opt/stocktrack/docker-compose.yml up -d
```

---

## Cost Breakdown

| Component | Price | Notes |
|-----------|-------|-------|
| Droplet (1 vCPU, 1 GB) | **$6/month** | 25 GB SSD, 1 TB transfer |
| Droplet backups (optional) | $1.20/month | Weekly full-server snapshots |
| Custom domain | $10-15/year | From registrar |
| SSL certificate | Free | Let's Encrypt via Certbot |
| **Total** | **~$6-8/month** | Half the cost of App Platform |

---

## Next Steps After Deployment

1. ✅ Test the app thoroughly at your domain
2. ✅ Test login with all user accounts from `users.yaml`
3. ✅ Create real storerooms, properties, and stock items
4. ✅ Enable DigitalOcean Droplet backups ($1.20/month)
5. ✅ Share the URL with your team
6. ✅ Change the default passwords in `users.yaml` and redeploy
7. ✅ Set a reminder to check logs and backups weekly

---

## Support & Resources

- **DigitalOcean Droplets:** https://docs.digitalocean.com/products/droplets/
- **Docker Compose:** https://docs.docker.com/compose/
- **Nginx:** https://nginx.org/en/docs/
- **Certbot (SSL):** https://certbot.eff.org/
- **Streamlit Deployment:** https://docs.streamlit.io/deploy

---

**Your StockTrack app is now in production on a $6/month server with persistent storage, SSL, and automated backups.**
