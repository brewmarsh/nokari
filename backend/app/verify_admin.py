import sys
import logging
from backend.app.firebase_config import db
from backend.app.firebase_auth_repo import FirebaseAuthRepo
from backend.app.firestore_repo import FirestoreRepo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_admin_role(email: str):
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
        logger.error(f"User document NOT found in Firestore for UID: {uid}")
    else:
        role = user_doc.get("role")
        logger.info(f"User document found. Role: {role}")
        if role == "admin":
            logger.info("VERIFICATION SUCCESS: User has 'admin' role.")
        else:
            logger.warning(
                f"VERIFICATION FAILED: User has role '{role}', expected 'admin'."
            )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m backend.app.verify_admin <email>")
        sys.exit(1)

    email_arg = sys.argv[1]
    verify_admin_role(email_arg)
