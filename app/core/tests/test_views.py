from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationTest(APITestCase):
    def test_registration(self):
        """
        Ensure we can create a new user.
        """
        url = reverse('register')
        data = {'email': 'test@example.com', 'password': 'somepassword', 'role': 'user'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')
