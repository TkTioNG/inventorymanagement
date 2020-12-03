from faker import Faker
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from inventory.models import Material, MaterialStock
from inventory.tests.factories import UserFactory, StoreFactory, MaterialStockFactory
from inventory.services.restock import get_restock_total_price
from inventory.utils import get_model_obj_property


class TokenAuthorizationTestCases(APITestCase):
    """Testing for the token authentication"""

    def setUp(self):
        """Create an user and the token"""
        faker = Faker()
        password = faker.pystr(min_chars=8, max_chars=16)
        self.user = UserFactory.create(password=password)
        self.token = Token.objects.create(user=self.user)

        self.store = StoreFactory(user=self.user)
        self.material_stock = MaterialStockFactory.create_batch(
            3,
            store=self.store,
            max_capacity=2000,
            current_capacity=1000
        )
        self.data = self._get_formatted_data(self.material_stock)
        self.post_data = self._get_formatted_data(
            self.material_stock,
            quantity=50
        )

    def test_get_with_auth(self):
        """GET restock endpoint with token authorization"""
        response = self.client.get(
            '/api/v1/restock/',
            HTTP_AUTHORIZATION='Token {}'.format(self.token)
        )

        # Access allow
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json(), self.data)

    def test_get_without_auth(self):
        """GET restock endpoint without token authorization"""
        response = self.client.get('/api/v1/restock/')

        # Verify access denied
        self.assertEqual(response.status_code, 401)

    def test_get_with_wrong_auth(self):
        """GET restock endpoint with wrong token authorization"""
        response = self.client.get(
            '/api/v1/restock/',
            HTTP_AUTHORIZATION='Token {}'.format(Faker().pyint())
        )

        # Verify access denied
        self.assertEqual(response.status_code, 401)

    def test_post_with_auth(self):
        """POST restock endpoint with token authorization"""
        response = self.client.post(
            '/api/v1/restock/',
            data=self.post_data,
            format='json',
            HTTP_AUTHORIZATION='Token {}'.format(self.token)
        )

        # Verify access
        self.assertEqual(response.status_code, 200)

        # Retrieve updated object
        material_stocks = MaterialStock.objects.filter(pk__lte=3)
        # Get serialized format
        updated_data = self._get_formatted_data(material_stocks)

        # Verify response content
        self.assertEqual(response.json(), updated_data)

        # Verify database update
        for material_stock in material_stocks:
            # Make sure that the capacity is updated correctly
            self.assertEqual(material_stock.max_capacity, 2000)
            self.assertEqual(material_stock.current_capacity, 1050)

    def test_post_without_auth(self):
        """POST restock endpoint without token authorization"""
        response = self.client.post(
            '/api/v1/restock/',
            data=self.post_data,
            format='json'
        )

        # Verify access denial
        self.assertEqual(response.status_code, 401)

    def test_post_with_wrong_auth(self):
        """POST restock endpoint with wrong token authorization"""
        response = self.client.post(
            '/api/v1/restock/',
            data=self.post_data,
            format='json',
            HTTP_AUTHORIZATION='Token {}'.format(Faker().pyint())
        )

        # Verify access denial
        self.assertEqual(response.status_code, 401)

    def test_put_with_auth(self):
        """PUT material stock endpoint with valid token authentication"""

        ms_obj = self._get_material_stock()

        # Convert model object to serialized format
        original_data = self._get_ms_obj_property(ms_obj)

        # Update max_capacity
        updated_data = {
            **original_data,
            "max_capacity": 4999,
        }

        response = self.client.put(
            '/api/v1/material-stock/{}/'.format(ms_obj.id),
            data=updated_data,
            format='json',
            HTTP_AUTHORIZATION='Token {}'.format(self.token)
        )

        # Verify access
        self.assertEqual(response.status_code, 200)

        # Verify response content
        self.assertEqual(response.json(), updated_data)

        ms_obj = MaterialStock.objects.get(pk=ms_obj.pk)

        # Verify database object updated
        self.assertEqual(self._get_ms_obj_property(ms_obj), updated_data)

    def test_put_without_auth(self):
        """PUT material stock endpoint without token authentication"""

        ms_obj = self._get_material_stock()

        # Convert model object to serialized format
        original_data = self._get_ms_obj_property(ms_obj)

        updated_data = {
            **original_data,
            "max_capacity": 4999,
        }

        response = self.client.put(
            '/api/v1/material-stock/{}/'.format(ms_obj.id),
            data=updated_data,
            format='json'
        )

        # Verify access
        self.assertEqual(response.status_code, 401)

    def test_put_with_wrong_auth(self):
        """PUT material stock endpoint with invalid token authentication"""

        ms_obj = self._get_material_stock()

        # Convert model object to serialized format
        original_data = self._get_ms_obj_property(ms_obj)

        updated_data = {
            **original_data,
            "max_capacity": 4999,
        }

        response = self.client.put(
            '/api/v1/material-stock/{}/'.format(ms_obj.id),
            data=updated_data,
            format='json',
            HTTP_AUTHORIZATION='Token {}'.format(Faker().pyint())
        )

        # Verify access
        self.assertEqual(response.status_code, 401)

    def test_delete_with_auth(self):
        """DELETE material stock endpoint with valid token authentication"""

        ms_obj = self._get_material_stock()

        response = self.client.delete(
            '/api/v1/material-stock/{}/'.format(ms_obj.id),
            HTTP_AUTHORIZATION='Token {}'.format(self.token)
        )

        # Verify access
        self.assertEqual(response.status_code, 204)

        # Retrieve obj from database
        ms_obj = MaterialStock.objects.filter(pk=ms_obj.pk)

        # Verify the object is removed from database
        self.assertEqual(ms_obj.count(), 0)

    def test_delete_without_auth(self):
        """DELETE material stock endpoint without token authentication"""

        ms_obj = self._get_material_stock()

        response = self.client.delete(
            '/api/v1/material-stock/{}/'.format(ms_obj.id)
        )

        # Verify access denial
        self.assertEqual(response.status_code, 401)

        # Retrieve obj from database
        ms_obj = MaterialStock.objects.filter(pk=ms_obj.pk)

        # Verify the object is still exist in the database
        self.assertEqual(ms_obj.count(), 1)

    def test_delete_with_wrong_auth(self):
        """DELETE material stock endpoint with invalid token authentication"""

        ms_obj = self._get_material_stock()

        response = self.client.delete(
            '/api/v1/material-stock/{}/'.format(ms_obj.id),
            HTTP_AUTHORIZATION='Token {}'.format(Faker().pyint())
        )

        # Verify access denial
        self.assertEqual(response.status_code, 401)

        # Retrieve obj from database
        ms_obj = MaterialStock.objects.filter(pk=ms_obj.pk)

        # Verify the object is still exist in the database
        self.assertEqual(ms_obj.count(), 1)

    def _get_formatted_data(self, ms_obj, quantity=0):
        """Update the serialized data with current MaterialStock obj"""
        materials_array = []
        for ms in ms_obj:
            if quantity == 0:
                materials_array.append({
                    "material": ms.material.material_id,
                    "quantity": ms.max_capacity - ms.current_capacity
                })
            else:
                materials_array.append({
                    "material": ms.material.material_id,
                    "quantity": quantity
                })

        total_price = 0
        for material in materials_array:
            if "material" in material or "quantity" in material:
                try:
                    price = Material.objects.get(
                        pk=material.get('material')
                    ).price
                    total_price += price * material.get('quantity')
                except Material.DoesNotExist:
                    raise ValueError("material is not found.")

        return {
            "materials": materials_array,
            "total_price": round(total_price, 2),
        }

    def _get_material_stock(self):
        """Return one MaterialStock obj"""
        return MaterialStockFactory(store=self.store)

    def _get_ms_obj_property(self, ms_obj):
        """Return properties of a MaterialStock obj in dict"""
        new_ms_obj = get_model_obj_property(MaterialStock, ms_obj)
        new_ms_obj["store"] = new_ms_obj["store"].pk
        new_ms_obj["material"] = new_ms_obj["material"].pk
        return new_ms_obj
