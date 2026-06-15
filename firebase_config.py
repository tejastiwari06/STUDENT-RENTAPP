import os
import firebase_admin
from firebase_admin import credentials, db

_app = None

def init_firebase():
    global _app
    if _app is not None:
        return _app

    cred_path = os.getenv("FIREBASE_CREDENTIALS", "serviceAccountKey.json")
    database_url = os.getenv("FIREBASE_DATABASE_URL", "")

    if not os.path.exists(cred_path):
        raise FileNotFoundError(
            f"Firebase credentials file not found: '{cred_path}'. "
            "Download your serviceAccountKey.json from Firebase Console → "
            "Project Settings → Service Accounts and place it in the project root."
        )

    cred = credentials.Certificate(cred_path)
    _app = firebase_admin.initialize_app(cred, {"databaseURL": database_url})
    return _app


def get_db_ref(path: str):
    return db.reference(path)
