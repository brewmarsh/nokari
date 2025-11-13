from firebase_admin import auth
from firebase_admin.auth import UserNotFoundError
from fastapi import HTTPException, status


class FirebaseAuthRepo:
    """
    A repository for interacting with Firebase Authentication.
    """

    def create_user(self, email: str, password: str) -> str:
        """
        Creates a new user in Firebase Authentication.
        Returns the user's UID.
        """
        try:
            user = auth.create_user(email=email, password=password)
            return user.uid
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Firebase user creation failed: {e}",
            )

    def get_user_by_email(self, email: str):
        """
        Retrieves a user by email from Firebase Authentication.
        """
        try:
            user = auth.get_user_by_email(email)
            return user
        except UserNotFoundError:
            return None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching user by email from Firebase: {e}",
            )

    def verify_id_token(self, id_token: str) -> dict:
        """
        Verifies a Firebase ID token and returns the decoded claims.
        """
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Firebase ID token: {e}",
            )
