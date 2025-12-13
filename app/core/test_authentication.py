from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from app.core.authentication import FirebaseAuthentication

User = get_user_model()

class FirebaseAuthenticationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.email = "test@example.com"
        self.uid = "firebase_uid_123"

    @patch("app.core.authentication.auth.verify_id_token")
    def test_authentication_success_existing_user(self, mock_verify):
        # Create user
        user = User.objects.create_user(email=self.email, username=self.email)

        # Mock Firebase verification
        mock_verify.return_value = {
            "email": self.email,
            "uid": self.uid
        }

        # Manually invoke authentication
        auth_backend = FirebaseAuthentication()

        # Mock request
        request = MagicMock()
        request.META = {"HTTP_AUTHORIZATION": "Bearer valid_token"}

        authenticated_user, _ = auth_backend.authenticate(request)

        self.assertEqual(authenticated_user, user)
        mock_verify.assert_called_with("valid_token")

    @patch("app.core.authentication.auth.verify_id_token")
    def test_authentication_success_creates_user(self, mock_verify):
        # Mock Firebase verification
        mock_verify.return_value = {
            "email": "new@example.com",
            "uid": "new_uid"
        }

        auth_backend = FirebaseAuthentication()
        request = MagicMock()
        request.META = {"HTTP_AUTHORIZATION": "Bearer new_token"}

        authenticated_user, _ = auth_backend.authenticate(request)

        self.assertEqual(authenticated_user.email, "new@example.com")
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    @patch("app.core.authentication.auth.verify_id_token")
    def test_authentication_failure(self, mock_verify):
        mock_verify.side_effect = Exception("Invalid token")

        auth_backend = FirebaseAuthentication()
        request = MagicMock()
        request.META = {"HTTP_AUTHORIZATION": "Bearer invalid_token"}

        result = auth_backend.authenticate(request)

        self.assertIsNone(result)
