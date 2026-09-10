"""
General helper utilities — password hashing, validation, status calculation.
Ported from the original Flask app.py.
"""

import hashlib
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# ─── Password Utilities ───────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Return SHA-256 hex digest of the given password string."""
    return hashlib.sha256(password.encode()).hexdigest()


def validate_password(password: str) -> bool:
    """
    Password must contain at least:
    - one letter
    - one digit
    - one special character
    """
    pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$'
    return bool(re.match(pattern, password))


# ─── Schedule / Status Helpers ────────────────────────────────────────────────

def get_current_lecture(schedule: dict) -> dict | None:
    """
    Return the current lecture details if the teacher is in class right now.

    Returns a dict: {"room": ..., "subject": ..., "time_slot": ...}
    or None if not currently in any lecture.
    """
    now = datetime.now()
    current_day = now.strftime("%A")
    current_time = now.strftime("%H:%M")  # 24-hour for comparison

    if current_day not in schedule:
        return None

    day_schedule = schedule[current_day]
    if isinstance(day_schedule, list):
        day_schedule = {str(i): room for i, room in enumerate(day_schedule)}

    for time_slot, entry in day_schedule.items():
        try:
            start, end = time_slot.split("-")
            if start <= current_time <= end:
                if isinstance(entry, dict):
                    room = entry.get("room", "")
                    subject = entry.get("subject", "")
                else:
                    parts = entry.split(" / ")
                    room = parts[0] if len(parts) > 0 else ""
                    subject = parts[1] if len(parts) > 1 else ""
                return {"room": room, "subject": subject, "time_slot": time_slot}
        except Exception:
            continue

    return None


def calculate_status(teacher: dict) -> tuple[str, str, str]:
    """
    Calculate the real-time status for a teacher based on their schedule.

    Returns (calculated_status, current_day, current_time_str)
    """
    now = datetime.now()
    current_day = now.strftime("%A")
    schedule = teacher.get("schedule", {}) or {}
    status = teacher.get("status", "Available")
    calculated_status = "Available"

    try:
        if current_day in schedule and isinstance(schedule[current_day], dict):
            for time_slot, room_subject in schedule[current_day].items():
                try:
                    start, end = time_slot.split("-")
                    if start <= now.strftime("%H:%M") <= end:
                        calculated_status = f"Busy in {room_subject}"
                        break
                except Exception:
                    continue
    except Exception:
        pass

    if "ON LEAVE" in str(status).upper():
        calculated_status = "On Leave"

    return calculated_status, current_day, now.strftime("%H:%M")


# ─── Default Data Setup ───────────────────────────────────────────────────────

def setup_defaults():
    """
    Ensure a default super admin exists in Firebase.
    Called once when Django starts (via AppConfig.ready).
    """
    import os
    db_url = os.environ.get("FIREBASE_DATABASE_URL", "").strip()
    if not db_url:
        logger.info("ℹ️ FIREBASE_DATABASE_URL not configured in .env. Skipping default admin seeding.")
        return

    from core.utils.firebase import db
    if db is None:
        logger.warning("Firebase not available, skipping setup_defaults.")
        return
    try:
        existing = db.child("admins").child("admin1").get().val()
        if not existing:
            db.child("admins").child("admin1").set({
                "name": "Super Admin",
                "password": hash_password("admin123")
            })
            logger.info("✅ Default admin created!")
        else:
            logger.info("ℹ️ Admin already exists, skipping setup.")
    except Exception as e:
        logger.warning("setup_defaults skipped: %s", e)
