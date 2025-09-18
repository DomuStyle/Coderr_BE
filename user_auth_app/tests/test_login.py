"""Test cases for the login API endpoint in Django REST Framework, covering happy and unhappy paths."""

from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token


class UserLoginAPItestCaseHappy(APITestCase):
    """Test cases for successful login scenarios."""

    def setUp(self):
        """Set up a test user for authentication testing."""
        # Create a test user for authentication testing.
        self.user = User.objects.create_user(
                username='exampleUsername',
                password='examplePassword'
            )
        
    def test_login_successful(self):   
        """Test successful login with valid credentials."""
        url = reverse('login')
        data = {
            "username": "exampleUsername",
            "password": "examplePassword"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserLoginAPItestCaseUnhappy(APITestCase):
    """Test cases for failed login scenarios."""
    
    def setUp(self):
        """Set up a test user for authentication testing."""
        # Create a test user for authentication testing.
        self.user = User.objects.create_user(
                username='exampleUsername',
                password='examplePassword'
            )
        
    def test_login_not_successful(self):   
        """Test login failure with incorrect password."""
        url = reverse('login')
        data = {
            "username": "exampleUsername",
            "password": "differentexamplePassword"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)