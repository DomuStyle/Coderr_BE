"""Test cases for the registration API endpoint in Django REST Framework, covering happy and unhappy paths."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient


class UserProfileAPItestCaseHappy(APITestCase):
    """Test cases for successful registration scenarios."""

    def setUp(self):
        """Set up a test client for registration testing."""
        # Initialize a test client for API requests.
        self.client = APIClient()

    def test_registration_successful(self):
        """Test successful registration with valid data."""
        url = reverse('registration')
        data = {
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UserProfileAPItestCaseUnhappy(APITestCase):
    """Test cases for failed registration scenarios."""

    def test_registration_fields_missing(self):
        """Test registration failure with missing required fields."""
        url = reverse('registration')
        data = {
            "username": "exampleUsername",
            "email": "example@mail.de",
            "type": "customer"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_passwords_dont_match(self):
        """Test registration failure with mismatched passwords."""
        url = reverse('registration')
        data = {
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "differentexamplePassword",
            "type": "customer"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)