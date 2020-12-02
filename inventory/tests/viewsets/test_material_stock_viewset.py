from inventory.tests.viewsets.base import BaseTestCase

from inventory.tests.factories import StoreFactory, MaterialStockFactory, ProductFactory, MaterialQuantityFactory
from inventory.models import MaterialStock
from inventory.utils import get_model_obj_property


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
            store=store,
            max_capacity=3000,
            current_capacity=100
        )
        self.data = {
            "id": material_stock.id,
            "max_capacity": 5000,
            "current_capacity": 50,
            "store": store.store_id,
            "material": material_stock.material.material_id,
        }
        self.invalid_data = {
            "id": material_stock.id,
            "max_capacity": 10,  # < current_capacity (100)
            "current_capacity": material_stock.current_capacity,
            "store": store.store_id,
            "material": material_stock.material.material_id,
        }

    def test_get_capacity(self):
        """Verify update of maximum capacity and inability to update current capacity"""
        response = self.client.get(
            '/api/v1/material-stock/',
            HTTP_AUTHORIZATION=self.formatted_token
        )

        # Verify access allow
        self.assertEqual(response.status_code, 200)

        # Get objects from database
        ms_objects = MaterialStock.objects.all()

        # Get expected results
        expected_params = self._get_expected_params(ms_objects, many=True)

        # Verify the material stock content and the current capacity is remained unchanged
        self.assertEqual(response.json(), expected_params)

    def test_update_capacity(self):
        """Verify update of maximum capacity and inability to update current capacity"""
        response = self.client.put(
            '/api/v1/material-stock/{}/'.format(self.data["id"]),
            data=self.data,
            format='json', HTTP_AUTHORIZATION=self.formatted_token
        )

        # Verify access allow
        self.assertEqual(response.status_code, 200)

        self.data["current_capacity"] = 100

        # Verify the material stock content and the current capacity is remained unchanged
        self.assertEqual(response.json(), self.data)

        # Get objects from database
        updated_object = MaterialStock.objects.last()

        # Get expected results
        expected_params = self._get_expected_params(updated_object)

        # Verify response content
        self.assertEqual(response.json(), expected_params)

        # Verify database obj updated correctly
        self.assertEqual(updated_object.max_capacity, 5000)
        self.assertEqual(updated_object.current_capacity, 100)

    def test_update_capacity_invalid(self):
        """Verify that do not updatewhen maximum capacity < current capacity"""
        response = self.client.put(
            '/api/v1/material-stock/{}/'.format(self.data["id"]),
            data=self.invalid_data,
            format='json',
            HTTP_AUTHORIZATION=self.formatted_token
        )

        # Verify operation denial
        self.assertEqual(response.status_code, 400)

    def _get_expected_params(self, ms_objects, many=False):
        """Get expected results"""
        if many:
            expected_params = []
            for ms_obj in ms_objects:
                expected_params.append(self._get_expected_ms_obj(ms_obj))
            return expected_params

        expected_params = self._get_expected_ms_obj(ms_objects)
        return expected_params

    def _get_expected_ms_obj(self, ms_obj):
        """Change foreign key from model obj to pk"""
        expected_ms_obj = get_model_obj_property(MaterialStock, ms_obj)
        expected_ms_obj["material"] = expected_ms_obj["material"].pk
        expected_ms_obj["store"] = expected_ms_obj["store"].pk
        return expected_ms_obj
