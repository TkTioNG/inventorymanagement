from inventory.tests.viewsets.base import BaseTestCase

from inventory.tests.factories import StoreFactory, MaterialStockFactory, ProductFactory, MaterialQuantityFactory


class MaterialStockTestCases(BaseTestCase):
    """Test the MaterialStock ViewSet with POST method, which include
       testing the update of maximum capacity and do not update the current capacity."""

    def setUp(self):
        """Create restock data"""
        super().setUp()
        # create Store
        store = StoreFactory.create(user=self.user)
        # Create material
        material_stock = MaterialStockFactory(
            store=store, max_capacity=3000, current_capacity=100)
        self.data = [
            {
                "id": material_stock.id,
                "max_capacity": 5000,
                "current_capacity": 50,
                "store": store.store_id,
                "material": material_stock.material.material_id,
            },
        ]
        self.invalid_data = [
            {
                "id": material_stock.id,
                "max_capacity": 10,  # < current_capacity (100)
                "current_capacity": material_stock.current_capacity,
                "store": store.store_id,
                "material": material_stock.material.material_id,
            },
        ]

    def test_update_capacity(self):
        """Verify update of maximum capacity and inability to update current capacity"""
        response = self.client.post('/api/v1/material-stock/', data=self.data, format='json',
                                    HTTP_AUTHORIZATION=self.formatted_token)

        # Verify access allow
        self.assertEqual(response.status_code, 200)

        self.data[0]["current_capacity"] = 100

        # Verify the material stock content and the current capacity is remained unchanged
        self.assertEqual(response.json(), self.data)

    def test_update_capacity_invalid(self):
        """Verify that do not updatewhen maximum capacity < current capacity"""
        response = self.client.post('/api/v1/material-stock/', data=self.invalid_data, format='json',
                                    HTTP_AUTHORIZATION=self.formatted_token)

        # Verify operation denial
        self.assertEqual(response.status_code, 400)

        expected_data = self.invalid_data
        expected_data[0]["maximum_capacity"] = 3000

        # Verify that the maximum capacity does not update
        self.assertEqual(response.json(), expected_data)
