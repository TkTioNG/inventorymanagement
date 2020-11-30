import factory
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from inventory.tests.factories import UserFactory


class BaseTestCase(APITestCase):
    def setUp(self):
        """Create an user and the token"""
        password = factory.Faker('pystr', min_chars=8, max_chars=16)
        self.user = UserFactory.create(password=password)
        self.token = Token.objects.create(user=self.user)
        self.formatted_token = 'Token {}'.format(self.token)
