"""
Centralised logging with rotation.
Import `logger` anywhere in the app.
"""
import logging
import logging.handlers
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def _build_logger() -> logging.Logger:
    log = logging.getLogger("stocktrack")
    if log.handlers:          # already configured — don't add twice
        return log

    log.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(module)s:%(lineno)d  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Rotating file — 5 MB per file, keep 7 backups ────────
    fh = logging.handlers.RotatingFileHandler(
        LOG_DIR / "stocktrack.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=7,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    # ── Error-only file for quick triage ─────────────────────
    eh = logging.handlers.RotatingFileHandler(
        LOG_DIR / "errors.log",
        maxBytes=2 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    eh.setLevel(logging.ERROR)
    eh.setFormatter(fmt)

    # ── Console (shows in `streamlit run` terminal) ───────────
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    log.addHandler(fh)
    log.addHandler(eh)
    log.addHandler(ch)
    return log


logger = _build_logger()
