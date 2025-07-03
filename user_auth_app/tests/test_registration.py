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
    pass


class UserProfileAPItestCaseUnhappy(APITestCase):
    pass