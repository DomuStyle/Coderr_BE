# standard bib imports
from django.urls import reverse
from django.contrib.auth.models import User

# third party imports
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

# local imports
from user_auth_app.models import UserProfile


class UserProfileAPItestCaseHappy(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_registration_successful(self):
        url = reverse('registration')

        data = {
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer"
        }
    
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
class UserProfileAPItestCaseUnhappy(APITestCase):
    
    def test_registration_fields_missing(self):
        url = reverse('registration')

        data = {
            "username": "exampleUsername",
            "email": "example@mail.de",
            "type": "customer"
        }
    
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_registration_passwords_dont_match(self):
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