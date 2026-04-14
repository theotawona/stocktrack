# Production Deployment Checklist

Use this checklist to track your deployment progress.

## Pre-Deployment (Do These Now)

- [ ] **Review DEPLOYMENT_GUIDE.md** thoroughly
- [ ] **Test the app locally:**
  ```bash
  docker compose up --build
  # Visit http://localhost:8501 and test all features
  ```
- [ ] **Commit all deployment files to GitHub:**
  ```bash
  git add Dockerfile .dockerignore docker-compose.yml backup_database.py
  git commit -m "Add production deployment configuration"
  git push
  ```

## Deployment (Follow These Steps)

### Account & Droplet Setup
- [ ] Create DigitalOcean account
- [ ] Add payment method
- [ ] Create SSH key (if you don't have one)
- [ ] Create Droplet: Ubuntu 24.04 LTS, $6/month (1 vCPU, 1 GB RAM)
- [ ] Note the Droplet IP address: `_______________`

### Server Setup (SSH into Droplet)
- [ ] SSH in: `ssh root@YOUR_IP`
- [ ] Install Docker: `curl -fsSL https://get.docker.com | sh`
- [ ] Install Docker Compose: `apt install -y docker-compose-plugin`
- [ ] Install Nginx: `apt install -y nginx certbot python3-certbot-nginx`
- [ ] Configure firewall: `ufw allow OpenSSH; ufw allow 'Nginx Full'; ufw enable`

### Deploy StockTrack
- [ ] Clone repo: `cd /opt && git clone https://github.com/theotawona/stocktrack.git`
- [ ] Build & start: `cd stocktrack && docker compose up -d --build`
- [ ] Verify running: `docker compose ps` and `curl http://localhost:8501/_stcore/health`

### Nginx & SSL
- [ ] Create Nginx config: `/etc/nginx/sites-available/stocktrack`
- [ ] Enable site and remove default config
- [ ] Test Nginx: `nginx -t && systemctl reload nginx`
- [ ] Verify app loads at `http://YOUR_DROPLET_IP`
- [ ] (After domain setup) Get SSL: `certbot --nginx -d YOUR_DOMAIN`

### Domain Configuration
- [ ] Add A record at your domain registrar pointing to Droplet IP
- [ ] Wait for DNS propagation (15 min to 48 hours)
- [ ] Update Nginx `server_name` with your domain
- [ ] Run Certbot for HTTPS

### Backups
- [ ] Create backup script: `/opt/backup-stocktrack.sh`
- [ ] Schedule daily cron job
- [ ] Test backup works: `/opt/backup-stocktrack.sh`
- [ ] (Optional) Enable DigitalOcean Droplet Backups ($1.20/month)

### Post-Deployment
- [ ] Test login with all user accounts
- [ ] Test stock management features
- [ ] Test requisitions and approvals
- [ ] Test invoice uploads
- [ ] Create deploy script: `/opt/stocktrack/deploy.sh`
- [ ] Verify app loads over HTTPS with your domain

## Ongoing Maintenance

### Weekly
- [ ] Check logs: `docker compose -f /opt/stocktrack/docker-compose.yml logs --tail 50`
- [ ] Verify backups exist: `ls -la /opt/stocktrack-backups/`
- [ ] Monitor DigitalOcean billing

### Monthly
- [ ] Check disk usage: `df -h`
- [ ] Check for Streamlit/dependency updates
- [ ] Test a manual restore of backup
- [ ] Review server resources: `free -h`

### Quarterly
- [ ] Update server packages: `apt update && apt upgrade -y`
- [ ] Verify SSL certificate auto-renewal: `certbot renew --dry-run`
- [ ] Audit user access
- [ ] Clean old Docker images: `docker system prune`

## Troubleshooting Reference

If you encounter issues:
1. Check [Troubleshooting section in DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#troubleshooting)
2. View logs: `docker compose logs -f`
3. Test locally: `docker compose up --build`

---

## Key Information to Save

Once deployed, save these for future reference:

```
Droplet IP: _________________
SSH Key Name: _________________
Custom Domain: _________________
App URL (final): _________________
Deploy Script: /opt/stocktrack/deploy.sh
Backup Script: /opt/backup-stocktrack.sh
Backup Location: /opt/stocktrack-backups/
```

## Cost Tracker

| When | Service | Cost | Notes |
|------|---------|------|-------|
| Monthly | Droplet (1 vCPU, 1 GB) | $6 | 25 GB SSD, persistent disk |
| Monthly | Droplet Backups (optional) | $1.20 | Weekly full snapshots |
| Yearly | Custom Domain | $10-15 | From registrar |

**Expected Monthly Cost: $6-8**

---

## Support

- **Stuck?** Read DEPLOYMENT_GUIDE.md → Troubleshooting
- **Need help?** DigitalOcean support: https://www.digitalocean.com/support
- **Documentation:** https://docs.digitalocean.com/products/droplets/

---

**Status:** Ready for deployment ✅
**Last Updated:** 2026-04-14
**Next Action:** Follow Step 1 in DEPLOYMENT_GUIDE.md
