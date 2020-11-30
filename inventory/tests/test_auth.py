import factory
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from inventory.tests.factories import UserFactory, StoreFactory, MaterialStockFactory
from inventory.utils import get_restock_total_price


class TokenAuthorizationTestCases(APITestCase):
    """Testing for the token authentication"""

    def setUp(self):
        """Create an user and the token"""
        password = factory.Faker('pystr', min_chars=8, max_chars=16)
        self.user = UserFactory.create(password=password)
        self.token = Token.objects.create(user=self.user)

    def test_get_with_auth(self):
        """GET restock endpoint with token authorization"""
        store = StoreFactory(user=self.user)
        material_stock = MaterialStockFactory.create_batch(3, store=store)
        response = self.client.get(
            '/api/v1/restock/', HTTP_AUTHORIZATION='Token {}'.format(self.token))

        # Access allow
        self.assertEqual(response.status_code, 200)

        expected_params = {
            "materials": [],  # TODO: Update materials
            "total_price": get_restock_total_price(material_stock),
        }

        self.assertEqual(response.json(), expected_params)

    def test_get_without_auth(self):
        """GET restock endpoint without token authorization"""
        response = self.client.get('/api/v1/restock/')

        # Verify access denied
        self.assertEqual(response.status_code, 401)

    def test_get_with_wrong_auth(self):
        """GET restock endpoint with wrong token authorization"""
        response = self.client.get(
            '/api/v1/restock/', HTTP_AUTHORIZATION='Token {}'.format(factory.Faker('pyint')))
        # Verify access denied
        self.assertEqual(response.status_code, 401)

    def test_post_with_auth(self):
        """POST restock endpoint with token authorization"""
        store = StoreFactory(user=self.user)
        material_stocks = MaterialStockFactory.create_batch(3, store=store)

        post_data = {
            "materials": [],  # TODO: Update materials array
        }

        response = self.client.post(
            '/api/v1/restock/', data=post_data, HTTP_AUTHORIZATION='Token {}'.format(self.token))

        # Verify access
        self.assertEqual(response.status_code, 200)

        # TODO: Update expected restock params
        expected_params = {
            "materials": [],
            "total_price": 0,
        }
        # Verify response content
        self.assertEqual(response.json(), expected_params)

    def test_post_without_auth(self):
        """POST restock endpoint without token authorization"""
        response = self.client.post('/api/v1/restock/')

        # Verify access denial
        self.assertEqual(response.status_code, 401)

    def test_post_with_wrong_auth(self):
        """POST restock endpoint with wrong token authorization"""
        response = self.client.post(
            '/api/v1/restock/', HTTP_AUTHORIZATION='Token {}'.format(factory.Faker('pyint')))

        # Verify access denial
        self.assertEqual(response.status_code, 401)
