import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
import os
import json

# Load Firebase Service Account Key from environment variable
firebase_credentials_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
if not firebase_credentials_json:
    raise ValueError("FIREBASE_CREDENTIALS_JSON environment variable not set.")

try:
    # The private key needs to have its newlines properly escaped.
    # If the value is coming from a JSON string, it should be fine.
    # However, if it's being set directly as a string in some environments,
    # we might need to handle escaped newlines. Let's assume it's a valid JSON string for now.
    FIREBASE_SERVICE_ACCOUNT_KEY = json.loads(firebase_credentials_json)

    # In some shell environments, newlines in the private key might get replaced
    # with literal '\n'. Let's fix that.
    if 'private_key' in FIREBASE_SERVICE_ACCOUNT_KEY:
        FIREBASE_SERVICE_ACCOUNT_KEY['private_key'] = FIREBASE_SERVICE_ACCOUNT_KEY['private_key'].replace('\\n', '\n')

except json.JSONDecodeError as e:
    raise ValueError(f"Could not decode FIREBASE_CREDENTIALS_JSON: {e}")

# Initialize Firebase Admin SDK
try:
    cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_KEY)
    firebase_admin.initialize_app(cred, {'storageBucket': f"{FIREBASE_SERVICE_ACCOUNT_KEY['project_id']}.appspot.com"})
    print("Firebase Admin SDK initialized successfully.")
except ValueError as e:
    print(f"Error initializing Firebase Admin SDK: {e}")
    # If the app is already initialized, we can ignore the error
    if "The default Firebase app already exists" not in str(e):
        raise

db = firestore.client()
firebase_auth = auth
firebase_storage = storage
