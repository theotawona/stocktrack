# 🚀 StockTrack Production Deployment Guide

**Deployment Target:** DigitalOcean App Platform  
**Tech Stack:** Docker + Streamlit + SQLite  
**Estimated Cost:** $12/month (basic tier) + custom domain  
**Estimated Setup Time:** 30-45 minutes

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Step 1: Prepare Your GitHub Repository](#step-1-prepare-your-github-repository)
3. [Step 2: Set Up DigitalOcean Account](#step-2-set-up-digitalocean-account)
4. [Step 3: Configure Custom Domain](#step-3-configure-custom-domain)
5. [Step 4: Deploy to DigitalOcean](#step-4-deploy-to-digitalocean)
6. [Step 5: Set Up Automatic Backups](#step-5-set-up-automatic-backups)
7. [Step 6: Monitor & Maintain](#step-6-monitor--maintain)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- ✅ GitHub account (free)
- ✅ DigitalOcean account ($12+ balance)
- ✅ Custom domain (optional but recommended)
- ✅ These files in your repo:
  - `Dockerfile` ✓ Created
  - `.dockerignore` ✓ Created
  - `app.yaml` ✓ Created
  - `backup_database.py` ✓ Created

---

## Step 1: Prepare Your GitHub Repository

### 1.1 Create a GitHub Repository

```bash
# If not already a git repo:
cd StockTrack
git init
git add .
git commit -m "Initial commit: StockTrack MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/stocktrack.git
git push -u origin main
```

### 1.2 Update `app.yaml` (IMPORTANT)

Edit `app.yaml` and replace:
```yaml
# Line 4: Replace with your GitHub repo
repo: YOUR_GITHUB_USERNAME/stocktrack

# Line 34: Replace with your custom domain
domain: your-domain.com  # e.g., stocktrack.company.com
```

### 1.3 Commit the deployment files

```bash
git add Dockerfile .dockerignore app.yaml backup_database.py
git commit -m "Add production deployment configuration"
git push
```

---

## Step 2: Set Up DigitalOcean Account

### 2.1 Create Account & Add Payment Method
1. Go to [digitalocean.com](https://digitalocean.com)
2. Sign up for a free account
3. Add a payment method (credit card)
4. Create a DigitalOcean Personal Access Token:
   - Go to Settings → API → Tokens/Keys
   - Click "Generate New Token"
   - Name it "stocktrack-deployment"
   - Select "Read" scope for now
   - Copy the token (you'll need it)

### 2.2 Create a GitHub Connection (for auto-deploy)
1. In DigitalOcean, go to Settings → GitHub
2. Click "Connect to GitHub"
3. Authorize DigitalOcean to access your repositories
4. Select your `stocktrack` repository

---

## Step 3: Configure Custom Domain

### 3.1 Set Up Your Domain

**Option A: Using a Domain You Own**
1. Go to your domain registrar (GoDaddy, Namecheap, etc.)
2. Find DNS settings
3. Create an `A` record:
   - **Name:** `stocktrack` (or your subdomain)
   - **Type:** `A`
   - **Value:** `(You'll get this from DigitalOcean after deployment)`

**Option B: Use DigitalOcean's Free SSL**
- DigitalOcean provides free SSL certificates
- Point your domain's nameservers to DigitalOcean's nameservers
- Instructions: DigitalOcean Dashboard → Networking → Domains

### 3.2 Add Domain to DigitalOcean
1. DigitalOcean Dashboard → Networking → Domains
2. Click "Add Domain"
3. Enter your domain name
4. DigitalOcean will provide nameservers
5. Update your domain registrar's nameservers (15-48 hours to propagate)

---

## Step 4: Deploy to DigitalOcean

### 4.1 Deploy Using App Platform

**Method 1: Using Web Console (Easiest)**

1. Go to DigitalOcean Dashboard → Apps
2. Click "Create App"
3. Choose "GitHub" source
4. Select your GitHub account
5. Find and select `stocktrack` repository
6. Choose `main` branch
7. DigitalOcean detects your `Dockerfile` automatically
8. Review configuration:
   - **Instance Size:** "Basic" ($12/month) ✅
   - **Port:** 8501 ✅
   - **Health Check:** `/_stcore/health` ✅
9. Click "Next"
10. Set environment variables:
    ```
    STREAMLIT_SERVER_HEADLESS=true
    STREAMLIT_SERVER_PORT=8501
    STREAMLIT_LOGGER_LEVEL=info
    ```
11. Click "Next" → Review → "Create Resources"
12. Wait for deployment (5-10 minutes)

**Method 2: Using CLI (If preferred)**

```bash
# Install doctl (DigitalOcean CLI)
# https://docs.digitalocean.com/reference/doctl/how-to/install/

# Authorize with DigitalOcean
doctl auth init

# Create app from your app.yaml
doctl apps create --spec app.yaml

# Get app status
doctl apps list
doctl apps get <app-id>
```

### 4.2 Verify Deployment

1. DigitalOcean will assign a temporary URL (e.g., `stocktrack-xxxxx.ondigitalocean.app`)
2. Test the app in your browser
3. Test login with your credentials from `users.yaml`
4. Verify database operations (create stock, requisitions, etc.)

### 4.3 Connect Custom Domain

1. Go to App → Settings → Domains
2. Add your custom domain
3. DigitalOcean provides DNS records to add
4. Update your domain registrar's DNS
5. SSL certificate is automatic (Let's Encrypt)
6. Wait 5-30 minutes for DNS propagation

---

## Step 5: Set Up Automatic Backups

### 5.1 Option A: DigitalOcean App Platform Persistent Storage (Recommended)

The `app.yaml` already includes volume configuration. Your SQLite database is stored at `/app/data/`.

**To back up manually:**
```bash
# Download from running app
doctl apps get <app-id> --format json | jq .
# Then use SCP or download from dashboard
```

### 5.2 Option B: Setup Cron Backup Job

Create a GitHub Actions workflow for automatic backups:

**File:** `.github/workflows/backup.yml`

```yaml
name: Database Backup

on:
  schedule:
    - cron: '0 2 * * *'  # Run daily at 2 AM UTC
  workflow_dispatch:

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Run backup
        env:
          DB_PATH: stock_tracker.db
        run: |
          python backup_database.py
      
      - name: Commit and push
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add data/backups/
          git commit -m "Daily backup: $(date)" || true
          git push
```

### 5.3 Option C: Cloud Storage Backup (Advanced)

To back up to DigitalOcean Spaces ($5/month):

1. Create Spaces bucket in DigitalOcean
2. Generate Access Key
3. Add to `app.yaml`:
   ```yaml
   envs:
   - key: ENABLE_CLOUD_BACKUP
     value: 'true'
   - key: SPACES_KEY
     value: ${SPACES_KEY}
   - key: SPACES_SECRET
     value: ${SPACES_SECRET}  # Store as secret
   - key: SPACES_BUCKET
     value: stocktrack-backups
   ```
4. In DigitalOcean: Apps → Settings → Encrypt these as secrets

---

## Step 6: Monitor & Maintain

### 6.1 View Logs
```bash
# In DigitalOcean Dashboard: Apps → Your App → Logs
# Or via CLI:
doctl apps logs <app-id>
```

### 6.2 Update Your App

When you push changes to GitHub:
1. DigitalOcean watches your `main` branch
2. Automatically rebuilds Docker image
3. Deploys new version (zero-downtime rolling update)
4. Takes ~5 minutes per update

### 6.3 Manual Restart
```bash
doctl apps restart <app-id>
```

### 6.4 Scale Up (If Needed)
1. DigitalOcean Dashboard → Apps → Your App → Settings
2. Change instance size (basic-xs → basic-s costs more)
3. For 6 users, basic-xs should be sufficient

### 6.5 Monitor Usage
1. Dashboard → Billing → Usage
2. Check bandwidth, compute hours
3. Set alerts for spending

---

## Troubleshooting

### App Won't Deploy
```
Error: Failed to build Docker image
```
**Solution:**
- Check `docker logs` locally: `docker build -t stocktrack .`
- Ensure all dependencies are in `requirements.txt`
- Check `Dockerfile` references correct Python version

### Database Errors After Deployment
```
Error: database is locked / unable to open database file
```
**Solution:**
- SQLite doesn't support network access
- Ensure database path is `/app/data/stock_tracker.db`
- Database is persisted via volume mount

### Custom Domain Not Working
```
Domain name mismatch / SSL certificate error
```
**Solution:**
- DNS propagation takes 15-48 hours
- Check DNS records: `nslookup your-domain.com`
- Use CloudFlare DNS checker: cloudflare.com/dns-checker
- Ensure A record points to DigitalOcean's IP

### Performance Issues
```
App is slow / timeouts
```
**Solution for 6 users on basic-xs:**
- Basic-xs (0.25 vCPU, 512MB) should handle 6 concurrent users
- Check logs for database locks
- Consider upgrading to `basic-s` ($18/month) if slow

### Backup Not Running
```
Backup files not created
```
**Solution:**
- Check GitHub Actions logs (if using Actions)
- Manually test: `python backup_database.py`
- Verify file permissions on `/app/data/`

---

## Cost Breakdown

| Component | Price | Notes |
|-----------|-------|-------|
| App Platform (basic-xs) | $12/month | 0.25 vCPU, 512MB RAM |
| Custom Domain | $10-15/year | From registrar (GoDaddy, etc.) |
| SSL Certificate | Free | Let's Encrypt (automatic) |
| Backups (local) | Free | Stored in app's volume |
| Backups (Spaces) | $5+/month | Only if using cloud storage |
| **Total MVP** | **~$12-14/month** | Custom domain included |

---

## Next Steps After Deployment

1. ✅ Test the app thoroughly in production
2. ✅ Set up monitoring alerts
3. ✅ Document any custom configurations
4. ✅ Train users on production URL
5. ✅ Update your `users.yaml` if needed
6. ✅ Plan backup strategy (GitHub Actions recommended for 6 users)
7. ✅ Set a reminder to review logs weekly

---

## Support & Resources

- **DigitalOcean Docs:** https://docs.digitalocean.com/products/app-platform/
- **Streamlit Deployment:** https://docs.streamlit.io/deploy
- **Docker Help:** https://docs.docker.com/
- **SQLite Persistent Storage:** https://github.com/streamlit/streamlit/issues/1018

---

**🎉 Congratulations!** Your StockTrack app is now in production!  
**Questions?** Check the [Troubleshooting](#troubleshooting) section or refer to DigitalOcean's documentation.
