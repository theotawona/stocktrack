# 🚀 Production Deployment Checklist

Use this checklist to track your deployment progress.

## Pre-Deployment (Do These Now)

- [ ] **Review DEPLOYMENT_GUIDE.md** thoroughly
- [ ] **Test the app locally:**
  ```bash
  docker build -t stocktrack .
  docker run -p 8501:8501 stocktrack
  # Visit http://localhost:8501 and test all features
  ```
- [ ] **Update app.yaml with:**
  - [ ] Your GitHub username in the `repo` field
  - [ ] Your custom domain in the `domain` field
- [ ] **Commit all deployment files to GitHub:**
  ```bash
  git add Dockerfile .dockerignore app.yaml backup_database.py DEPLOYMENT_GUIDE.md
  git commit -m "Add production deployment configuration"
  git push
  ```

## Deployment (Follow These Steps)

### Account Setup
- [ ] Create DigitalOcean account (free trial available)
- [ ] Add payment method
- [ ] Generate Personal Access Token
- [ ] Connect GitHub to DigitalOcean

### Domain Configuration
- [ ] Purchase/prepare custom domain (if using one)
- [ ] Add domain to DigitalOcean Networking
- [ ] Update domain registrar's nameservers (if needed)
- [ ] OR point A record to DigitalOcean's IP

### Deploy App
- [ ] Create new App in DigitalOcean
- [ ] Select GitHub as source
- [ ] Choose `stocktrack` repo and `main` branch
- [ ] Review container configuration (port 8501)
- [ ] Set environment variables
- [ ] Deploy (wait 5-10 minutes)

### Post-Deployment
- [ ] Test app at temporary DigitalOcean URL
- [ ] Verify login works
- [ ] Test core features (stock, requisitions)
- [ ] Check database operations
- [ ] Add custom domain to app
- [ ] Wait for DNS propagation (15-48 hours)
- [ ] Test at custom domain with HTTPS

## Ongoing Maintenance

### Weekly
- [ ] Check app logs for errors: `doctl apps logs <app-id>`
- [ ] Verify backups are created
- [ ] Monitor DigitalOcean billing

### Monthly
- [ ] Review app performance metrics
- [ ] Check for Streamlit updates
- [ ] Update dependencies if needed
- [ ] Test a manual restore of backup

### Quarterly
- [ ] Review security settings
- [ ] Check SSL certificate validity
- [ ] Audit user access logs
- [ ] Plan any infrastructure upgrades

## Backup Strategy (Choose One)

- [ ] **Option A (Recommended):** Use GitHub Actions + repository (see DEPLOYMENT_GUIDE.md)
- [ ] **Option B:** Manual backups to DigitalOcean Spaces
- [ ] **Option C:** Regular manual downloads

## Troubleshooting Reference

If you encounter issues:
1. Check [Troubleshooting section in DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#troubleshooting)
2. View logs: DigitalOcean Dashboard → Apps → Your App → Logs
3. Test locally: `docker build` and `docker run`

---

## Key Information to Save

Once deployed, save these for future reference:

```
App ID: _________________
GitHub Webhook URL: _________________
Custom Domain: _________________
DigitalOcean SSH Key Name: _________________
App URL (temp): _________________
App URL (custom): _________________
```

## Cost Tracker

| When | Service | Cost | Notes |
|------|---------|------|-------|
| Monthly | App Platform (basic-xs) | $12 | 0.25 vCPU, 512MB RAM |
| Yearly (or one-time) | Custom Domain | $10-15 | From registrar |
| Monthly (if added) | Cloud Backups (Spaces) | $5+ | Optional |

**Expected Monthly Cost: $12-14**

---

## Support

- **Stuck?** Read DEPLOYMENT_GUIDE.md → Troubleshooting
- **Need help?** DigitalOcean support: https://www.digitalocean.com/support
- **Documentation:** https://docs.digitalocean.com/products/app-platform/

---

**Status:** Ready for deployment ✅
**Last Updated:** 2026-04-13
**Next Action:** Follow Step 1 in DEPLOYMENT_GUIDE.md
