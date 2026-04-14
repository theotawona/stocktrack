#!/usr/bin/env python3
"""
SQLite Backup Script for StockTrack
Backs up the database to DigitalOcean Spaces or local storage
Run this as a cron job: 0 2 * * * /app/backup_database.py
"""

import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DB_PATH = Path(os.environ.get("DB_PATH", Path(__file__).parent / "stock_tracker.db"))
BACKUP_DIR = Path(os.environ.get("BACKUP_DIR", Path(__file__).parent / "data" / "backups"))
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Optional: Configure for cloud backup (DigitalOcean Spaces, AWS S3, etc.)
# For MVP, we'll do local backups and sync via git or manual transfer
ENABLE_CLOUD_BACKUP = os.getenv("ENABLE_CLOUD_BACKUP", "false").lower() == "true"

def backup_sqlite():
    """Create a backup of SQLite database"""
    try:
        if not DB_PATH.exists():
            print(f"❌ Database not found at {DB_PATH}")
            return False
        
        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"stock_tracker_backup_{timestamp}.db"
        
        # Use SQLite backup API for consistency (no locks)
        source_conn = sqlite3.connect(DB_PATH)
        source_conn.isolation_level = None
        backup_conn = sqlite3.connect(backup_file)
        
        with backup_conn:
            source_conn.backup(backup_conn)
        
        source_conn.close()
        backup_conn.close()
        
        file_size_mb = backup_file.stat().st_size / (1024 * 1024)
        print(f"✅ Backup created: {backup_file.name} ({file_size_mb:.2f} MB)")
        
        # Clean old backups (keep last 30 days)
        cleanup_old_backups(days=30)
        
        return True
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def cleanup_old_backups(days=30):
    """Remove backups older than specified days"""
    try:
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for backup_file in BACKUP_DIR.glob("stock_tracker_backup_*.db"):
            file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if file_mtime < cutoff_date:
                backup_file.unlink()
                print(f"🗑️  Removed old backup: {backup_file.name}")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

def upload_to_cloud():
    """Upload backup to cloud storage (optional)
    Example for DigitalOcean Spaces:
    """
    if not ENABLE_CLOUD_BACKUP:
        return
    
    try:
        import boto3
        
        # DigitalOcean Spaces configuration
        spaces_key = os.getenv("SPACES_KEY")
        spaces_secret = os.getenv("SPACES_SECRET")
        spaces_region = os.getenv("SPACES_REGION", "nyc3")
        spaces_endpoint = os.getenv("SPACES_ENDPOINT")
        bucket_name = os.getenv("SPACES_BUCKET")
        
        if not all([spaces_key, spaces_secret, spaces_endpoint, bucket_name]):
            print("⚠️  Cloud backup enabled but credentials missing")
            return
        
        session = boto3.session.Session()
        client = session.client(
            's3',
            region_name=spaces_region,
            endpoint_url=spaces_endpoint,
            aws_access_key_id=spaces_key,
            aws_secret_access_key=spaces_secret
        )
        
        # Upload latest backup
        latest_backup = max(BACKUP_DIR.glob("stock_tracker_backup_*.db"))
        
        client.upload_file(
            str(latest_backup),
            bucket_name,
            f"backups/{latest_backup.name}",
            ExtraArgs={'ACL': 'private'}
        )
        
        print(f"☁️  Uploaded to Spaces: {latest_backup.name}")
        
    except ImportError:
        print("⚠️  boto3 not installed. Install with: pip install boto3")
    except Exception as e:
        print(f"❌ Cloud upload failed: {e}")

if __name__ == "__main__":
    print(f"🔄 Starting StockTrack database backup... ({datetime.now().isoformat()})")
    
    success = backup_sqlite()
    
    if ENABLE_CLOUD_BACKUP:
        upload_to_cloud()
    
    sys.exit(0 if success else 1)
