from inventory.tests.viewsets.base import BaseTestCase

from inventory.tests.factories import StoreFactory, MaterialStockFactory
from inventory.utils import get_restock_total_price


class RestockViewSetTestCases(BaseTestCase):
    """Testing the Restock ViewSet with GET and POST method, which include
       serialized format, total_price and update of current_capacity (>= 0 && <= max_capacity"""

    def setUp(self):
        """Create restock data"""
        super().setUp()
        store = StoreFactory(user=self.user)
        self.data = MaterialStockFactory.create_batch(
            3, store=store, current_capacity=10, max_capacity=100)

    def modify_data_quantity(self, quantity=50):
        """Modify the current capacity of the MaterialStock object"""
        array = []
        for dt in self.data:
            array.append({
                "material": dt.material.material_id,
                "quantity": quantity
            })
        return array

    def test_get_restock(self):
        """Verify that the material stock and the total price are correctly serialized"""
        response = self.client.get('/api/v1/restock/',
                                   HTTP_AUTHORIZATION=self.formatted_token)

        # Access allow
        self.assertEqual(response.status_code, 200)

        # TODO: Update materials
        # material = RestockSerializer(instance=self.data, many=True).data
        expected_params = {
            "materials": [],
            "total_price": get_restock_total_price(self.data),
        }

        self.assertEqual(response.json(), expected_params)

    def test_post_restock(self):
        """Verify that update of the stock quantity with valid data"""

        post_data = {
            "materials": self.modify_data_quantity(),
        }

        response = self.client.post(
            '/api/v1/restock/', data=post_data, format='json', HTTP_AUTHORIZATION=self.formatted_token)

        # Verify access
        self.assertEqual(response.status_code, 200)

        # TODO: Update expected restock params from serializer
        # material = RestockSerializer(instance=self.data, many=True).data
        expected_params = {
            "materials": [],
            "total_price": get_restock_total_price(self.data),
        }
        # Verify response content
        self.assertEqual(response.json(), expected_params)

    def test_post_restock_exceed(self):
        """Verify that stock quantity does not update when current capacity > max_capacity"""

        # current_capacity > max_capacity (100)
        post_data = {
            "materials": self.modify_data_quantity(101),
        }

        response = self.client.post(
            '/api/v1/restock/', data=post_data, format='json', HTTP_AUTHORIZATION=self.formatted_token)

        # Verify bad request
        self.assertEqual(response.status_code, 400)

        # TODO: Update expected restock params from serializer
        # material = RestockSerializer(instance=self.data, many=True).data
        expected_params = {
            "materials": [],
            "total_price": get_restock_total_price(self.data),
        }
        # Verify response that the quantity do not update
        self.assertEqual(response.json(), expected_params)

    def test_post_restock_negative(self):
        """Verify that stock quantity does not update when current capacity < 0"""

        # current_capacity < 0
        post_data = {
            "materials": self.modify_data_quantity(-1),
        }

        response = self.client.post(
            '/api/v1/restock/', data=post_data, format='json', HTTP_AUTHORIZATION=self.formatted_token)

        # Verify bad request
        self.assertEqual(response.status_code, 400)

        # TODO: Update expected restock params from serializer
        # material = RestockSerializer(instance=self.data, many=True).data
        expected_params = {
            "materials": [],
            "total_price": get_restock_total_price(self.data),
        }
        # Verify response that the quantity do not update
        self.assertEqual(response.json(), expected_params)
