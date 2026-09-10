"""
Firebase initialization for the Django Monitoring System.
Uses pyrebase4 with credentials loaded from environment variables.
"""

import os
import logging
import pyrebase

logger = logging.getLogger(__name__)

_firebase_app = None
db = None


def get_firebase():
    """Lazily initialize and return the pyrebase Firebase app."""
    global _firebase_app, db
    if _firebase_app is None:
        config = {
            "apiKey": os.environ.get("FIREBASE_API_KEY", ""),
            "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN", ""),
            "databaseURL": os.environ.get("FIREBASE_DATABASE_URL", ""),
            "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET", ""),
        }
        _firebase_app = pyrebase.initialize_app(config)
        db = _firebase_app.database()
        logger.info("✅ Firebase initialized successfully.")
    return _firebase_app, db


# Initialize on module load so `db` is importable directly
try:
    _, db = get_firebase()
except Exception as e:
    logger.error("❌ Firebase initialization failed: %s", e)
    db = None
