# StockTrack - Deployment Ready

Your StockTrack app is ready for production deployment on a DigitalOcean Droplet.

## Quick Start

1. **Read the deployment guide:**
   - [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Complete step-by-step instructions

2. **Review the checklist:**
   - [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Track your deployment progress

3. **Test locally first:**
   ```bash
   docker compose up --build
   # Visit http://localhost:8501
   ```

4. **Deploy to a DigitalOcean Droplet:**
   - Follow [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) Steps 2-8

## Deployment Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Docker container definition |
| `docker-compose.yml` | Container orchestration with persistent volume |
| `.dockerignore` | Exclude files from Docker build |
| `backup_database.py` | SQLite backup utility |
| `DEPLOYMENT_GUIDE.md` | Complete deployment instructions |
| `DEPLOYMENT_CHECKLIST.md` | Step-by-step checklist |

## Why a Droplet?

StockTrack uses **SQLite** — a file-based database. A Droplet gives you a real persistent server where the database safely stays on disk across deployments and reboots. No workarounds needed.

## Expected Cost

- **$6/month** — DigitalOcean Droplet (1 vCPU, 1 GB RAM, 25 GB SSD)
- **$1.20/month** — Droplet weekly backups (optional, recommended)
- **$10-15/year** — Custom domain (from registrar)
- **Free** — SSL certificate (Let's Encrypt via Certbot)
- **Total: ~$6-8/month**

## What You Get

- Persistent SQLite storage on real disk
- Docker container with auto-restart
- Nginx reverse proxy with HTTPS
- Automated daily database backups
- Simple deploy script for updates (push to GitHub, run one command)
- Full SSH access to your server

## Prerequisites

- GitHub account (free) — repo already at `theotawona/stocktrack`
- DigitalOcean account ($6+ balance)
- Custom domain (optional but recommended)

## Setup Time

30-45 minutes from start to production.

## Documentation

- **Getting Started:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Progress Tracking:** [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

## Help

1. **Stuck?** Read the [Troubleshooting section](DEPLOYMENT_GUIDE.md#troubleshooting) in DEPLOYMENT_GUIDE.md
2. **DigitalOcean support:** https://www.digitalocean.com/support

---

**Status:** Ready for Production  
**Last Updated:** 2026-04-14  
**Framework:** Streamlit + Docker + Nginx  
**Database:** SQLite (persistent volume)  
**Server:** DigitalOcean Droplet ($6/month)
