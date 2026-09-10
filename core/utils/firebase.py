"""
Firebase initialization for the Django Monitoring System.
Uses pyrebase4 when credentials are provided in environment variables.
Provides an automatic local JSON database fallback when FIREBASE_DATABASE_URL
is not yet configured, allowing full local rendering, testing, and demonstration.
"""

import os
import json
import copy
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_firebase_app = None
db = None


# ─── Fallback Local Node Implementation (Pyrebase Compatible) ─────────────────

class PyrebaseVal:
    def __init__(self, data):
        self._data = data

    def val(self):
        return self._data


class LocalFirebaseNode:
    """Emulates the pyrebase child/get/set/update/remove interface using a local dict."""
    def __init__(self, root_data: dict, path: list = None, save_fn = None):
        self.root_data = root_data
        self.path = path or []
        self.save_fn = save_fn

    def child(self, name):
        return LocalFirebaseNode(self.root_data, self.path + [str(name)], self.save_fn)

    def _get_target(self, create=False):
        curr = self.root_data
        for part in self.path:
            if not isinstance(curr, dict):
                return None
            if part not in curr:
                if create:
                    curr[part] = {}
                else:
                    return None
            curr = curr[part]
        return curr

    def get(self):
        curr = self._get_target(create=False)
        return PyrebaseVal(copy.deepcopy(curr))

    def set(self, val):
        if not self.path:
            self.root_data.clear()
            if isinstance(val, dict):
                self.root_data.update(copy.deepcopy(val))
        else:
            curr = self.root_data
            for part in self.path[:-1]:
                if part not in curr or not isinstance(curr[part], dict):
                    curr[part] = {}
                curr = curr[part]
            curr[self.path[-1]] = copy.deepcopy(val)
        if self.save_fn:
            self.save_fn()
        return self

    def update(self, val):
        curr = self._get_target(create=True)
        if isinstance(curr, dict) and isinstance(val, dict):
            curr.update(copy.deepcopy(val))
        if self.save_fn:
            self.save_fn()
        return self

    def remove(self):
        if not self.path:
            self.root_data.clear()
        else:
            curr = self.root_data
            for part in self.path[:-1]:
                if part not in curr or not isinstance(curr[part], dict):
                    return self
                curr = curr[part]
            if isinstance(curr, dict) and self.path[-1] in curr:
                del curr[self.path[-1]]
        if self.save_fn:
            self.save_fn()
        return self


def _default_seed_data() -> dict:
    import hashlib
    def hp(p):
        return hashlib.sha256(p.encode()).hexdigest()

    return {
        "admins": {
            "admin1": {
                "name": "Super Admin",
                "password": hp("admin123")
            }
        },
        "teachers": {
            "T01": {
                "name": "Dr. Alan Turing",
                "password": hp("teach123!"),
                "status": "AVAILABLE",
                "last_updated": "Today 09:00 AM",
                "schedule": {
                    "Monday": {
                        "09:00-10:00": {"room": "Room 101", "subject": "CS101 - Algorithms"},
                        "11:00-12:00": {"room": "Lab 2", "subject": "CS201 - Data Structures"}
                    },
                    "Tuesday": {
                        "10:00-11:00": {"room": "Room 105", "subject": "CS301 - AI"}
                    },
                    "Wednesday": {
                        "09:00-10:00": {"room": "Room 101", "subject": "CS101 - Algorithms"}
                    },
                    "Thursday": {
                        "14:00-15:00": {"room": "Room 204", "subject": "CS401 - Operating Systems"}
                    },
                    "Friday": {
                        "11:00-12:00": {"room": "Lab 1", "subject": "CS202 - Networks"}
                    }
                }
            },
            "T02": {
                "name": "Prof. Ada Lovelace",
                "password": hp("teach123!"),
                "status": "ON LEAVE until Monday",
                "last_updated": "Today 08:30 AM",
                "schedule": {
                    "Tuesday": {
                        "09:00-10:00": {"room": "Room 202", "subject": "CS102 - Computer Architecture"}
                    }
                }
            }
        },
        "labs": {
            "lab1": {
                "name": "Main Computer Science Lab",
                "password": hp("lab123!"),
                "systems": 35,
                "issues": 3,
                "reports": {
                    "2026-09-10 09:30:00": {
                        "Monitors": 1,
                        "CPU": 0,
                        "Mouse": 2,
                        "Keyboard": 0,
                        "Switches": 0,
                        "OtherIssues": "Loose HDMI cable on Workstation 4"
                    }
                }
            },
            "lab2": {
                "name": "Electronics & Hardware Lab",
                "password": hp("lab123!"),
                "systems": 25,
                "issues": 0,
                "reports": {}
            }
        },
        "students": {
            "student1": {
                "name": "Demo Student",
                "password": hp("student123!")
            }
        }
    }


def get_firebase():
    """Return live Pyrebase client or local fallback database."""
    global _firebase_app, db
    if _firebase_app is not None and db is not None:
        return _firebase_app, db

    db_url = os.environ.get("FIREBASE_DATABASE_URL", "").strip()
    if db_url and (db_url.startswith("http://") or db_url.startswith("https://")):
        try:
            import pyrebase
            config = {
                "apiKey": os.environ.get("FIREBASE_API_KEY", ""),
                "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN", ""),
                "databaseURL": db_url,
                "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET", ""),
            }
            _firebase_app = pyrebase.initialize_app(config)
            db = _firebase_app.database()
            logger.info("✅ Connected to live Firebase Realtime Database.")
            return _firebase_app, db
        except Exception as e:
            logger.warning("⚠️ Live Firebase failed (%s); falling back to local database.", e)

    # Local fallback
    base_dir = Path(__file__).resolve().parent.parent.parent
    db_file = base_dir / "firebase_local.json"
    data = {}
    if db_file.exists():
        try:
            with open(db_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = _default_seed_data()
    else:
        data = _default_seed_data()

    def save():
        try:
            with open(db_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as err:
            logger.error("Error saving local database: %s", err)

    save()
    db = LocalFirebaseNode(data, save_fn=save)
    _firebase_app = "local"
    logger.info("ℹ️ Using local Firebase fallback database (%s).", db_file)
    return _firebase_app, db


# Initialize on module load
_, db = get_firebase()
