# standard bib imports
from django.urls import reverse
from django.contrib.auth.models import User

# third party imports
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

# local imports
from user_auth_app.models import UserProfile


class UserLoginAPItestCaseHappy(APITestCase):
     
    def setUp(self):

        self.user = User.objects.create_user(
                username='exampleUsername',
                password='examplePassword'
            )
        
    def test_login_successful(self):   

        url = reverse('login')
        data = {
            "username": "exampleUsername",
            "password": "examplePassword"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserLoginAPItestCaseUnhappy(APITestCase):
    
    def setUp(self):

        self.user = User.objects.create_user(
                username='exampleUsername',
                password='examplePassword'
            )
        
    def test_login_not_successful(self):   

        url = reverse('login')
        data = {
            "username": "exampleUsername",
            "password": "differentexamplePassword"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)