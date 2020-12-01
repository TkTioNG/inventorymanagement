from inventory.tests.viewsets.base import BaseTestCase

from inventory.tests.factories import StoreFactory, MaterialFactory, MaterialStockFactory
from inventory.serializers import MaterialSerializer


class MaterialTestCases(BaseTestCase):
    """Test the Material ViewSet with GET method, which include
       testing of serialized format for each materials in the store."""

    def setUp(self):
        """Create restock data"""
        super().setUp()
        store = StoreFactory(user=self.user)
        material1 = MaterialFactory()
        material2 = MaterialFactory()
        MaterialStockFactory(store=store, material=material1)
        MaterialStockFactory(store=store, material=material2)
        self.materials = [material1, material2]

    def test_get_products(self):
        """Verify the serialized format"""
        # percentage_of_capacity = decimal (XX.XX)
        response = self.client.get('/api/v1/material/',
                                   HTTP_AUTHORIZATION=self.formatted_token)

        # Verify access allowed
        self.assertEqual(response.status_code, 200)

        # Get expected results
        expected_params = MaterialSerializer(
            instance=self.materials, many=True).data

        # Verify serialized content
        self.assertEqual(response.json(), expected_params)
