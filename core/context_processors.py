import os

def clean_env(key: str) -> str:
    val = os.environ.get(key, "").strip()
    return val.strip('"').strip("'").strip()

def firebase_config(request):
    """Expose Firebase client configuration to Django templates."""
    auth_domain = clean_env("FIREBASE_AUTH_DOMAIN")
    project_id = clean_env("FIREBASE_PROJECT_ID")
    if not project_id and auth_domain:
        project_id = auth_domain.replace(".firebaseapp.com", "")

    return {
        "FIREBASE_CLIENT_CONFIG": {
            "apiKey": clean_env("FIREBASE_API_KEY"),
            "authDomain": auth_domain,
            "databaseURL": clean_env("FIREBASE_DATABASE_URL"),
            "projectId": project_id,
            "storageBucket": clean_env("FIREBASE_STORAGE_BUCKET"),
        }
    }
