import os
import json
import logging
import firebase_admin
from firebase_admin import credentials, auth
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework import exceptions

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
try:
    firebase_admin.get_app()
except ValueError:
    firebase_credentials_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    if firebase_credentials_json:
        try:
            # Handle potential newline escaping issues in private key
            service_account_info = json.loads(firebase_credentials_json)
            if "private_key" in service_account_info:
                service_account_info["private_key"] = service_account_info[
                    "private_key"
                ].replace("\\n", "\n")

            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing Firebase Admin SDK: {e}")
    else:
        logger.warning("FIREBASE_CREDENTIALS_JSON not found. Firebase Auth will not work.")

class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            return None

        parts = auth_header.split()
        if parts[0].lower() != "bearer":
            return None

        if len(parts) == 1:
            raise exceptions.AuthenticationFailed(
                "Invalid token header. No credentials provided."
            )
        elif len(parts) > 2:
            raise exceptions.AuthenticationFailed(
                "Invalid token header. Token string should not contain spaces."
            )

        token = parts[1]

        try:
            # verify_id_token raises generic Exception on failure (ValueError, auth.InvalidIdTokenError, etc)
            decoded_token = auth.verify_id_token(token)
        except Exception as e:
            logger.debug(f"Firebase token verification failed: {e}")
            # Return None to allow other authentication backends (like SimpleJWT) to try
            return None

        email = decoded_token.get("email")
        if not email:
            # If valid token but no email, that's weird.
            return None

        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Create user if not exists
            user = User.objects.create_user(email=email, username=email)

        return (user, None)
