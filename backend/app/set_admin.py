import sys
import logging
import json
import os
from backend.app.firebase_config import db
from backend.app.firebase_auth_repo import FirebaseAuthRepo
from backend.app.firestore_repo import FirestoreRepo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def set_admin_role(email: str):
    # Debug: Print Project ID
    try:
        creds_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
        if creds_json:
            creds = json.loads(creds_json)
            project_id = creds.get("project_id", "UNKNOWN")
            logger.info(f"Backend connected to Firebase Project ID: {project_id}")
        else:
            logger.warning(
                "FIREBASE_CREDENTIALS_JSON not found, cannot determine Project ID."
            )
    except Exception as e:
        logger.warning(f"Could not parse credentials to find Project ID: {e}")

    auth_repo = FirebaseAuthRepo()
    firestore_repo = FirestoreRepo(db_client=db)

    logger.info(f"Looking up user with email: {email}")
    user = auth_repo.get_user_by_email(email)

    if not user:
        logger.error(f"Error: No user found with email {email}")
        return

    uid = user.uid
    logger.info(f"Found user with UID: {uid}")

    user_doc = firestore_repo.get_user(uid)
    if not user_doc:
        logger.warning(
            f"User document not found in Firestore for UID: {uid}. Creating one..."
        )
        user_doc = {"email": email, "role": "admin", "created_at": None}
    else:
        logger.info(f"Current role: {user_doc.get('role', 'none')}")
        user_doc["role"] = "admin"

    firestore_repo.put_user(uid, user_doc)
    logger.info(f"Successfully set role to 'admin' for user {email} (UID: {uid})")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m backend.app.set_admin <email>")
        sys.exit(1)

    email_arg = sys.argv[1]
    set_admin_role(email_arg)
