from inventory.tests.viewsets.base import BaseTestCase

from inventory.tests.factories import StoreFactory, ProductFactory
from inventory.models import Product
from inventory.utils import get_model_obj_property


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
        expected_params = self._get_expected_params(self.products, many=True)

        # Verify serialized content
        self.assertEqual(response.json(), expected_params)

    def _get_expected_params(self, objects, many=False):
        """Get expected results"""
        if many:
            expected_params = []
            for obj in objects:
                expected_params.append(self._get_expected_obj(obj))
            return expected_params

        expected_params = self._get_expected_obj(objects)
        return expected_params

    def _get_expected_obj(self, obj):
        """Change foreign key from model obj to pk"""
        materials = obj.materials.all()
        expected_obj = get_model_obj_property(Product, obj)
        expected_obj["materials"] = [
            material.pk for material in materials
        ]
        return expected_obj
