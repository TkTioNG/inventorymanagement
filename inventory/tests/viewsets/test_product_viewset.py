from inventory.tests.viewsets.base import BaseTestCase

from inventory.tests.factories import StoreFactory, ProductFactory
from inventory.serializers import ProductSerializer


class ProductTestCases(BaseTestCase):
    """Test the Product ViewSet with GET method, which include
       testing of serialized format for each products in the store."""

    def setUp(self):
        """Create restock data"""
        super().setUp()
        self.products = ProductFactory.create_batch(3)
        store = StoreFactory(user=self.user, products=self.products)

    def test_get_products(self):
        """Verify the serialized format"""
        # percentage_of_capacity = decimal (XX.XX)
        response = self.client.get(
            '/api/v1/product/',
            HTTP_AUTHORIZATION=self.formatted_token
        )

        # Verify access allowed
        self.assertEqual(response.status_code, 200)

        # Get expected results
        expected_params = ProductSerializer(
            instance=self.products,
            many=True
        ).data

        # Verify serialized content
        self.assertEqual(response.json(), expected_params)
