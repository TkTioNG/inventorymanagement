from decimal import Decimal
from inventory.tests.viewsets.base import BaseTestCase

from inventory.tests.factories import StoreFactory, MaterialFactory, MaterialStockFactory
from inventory.models import Material
from inventory.utils import get_model_obj_property


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

    def test_get_materials(self):
        """Verify the serialized format"""
        response = self.client.get(
            '/api/v1/material/',
            HTTP_AUTHORIZATION=self.formatted_token
        )

        # Verify access allowed
        self.assertEqual(response.status_code, 200)

        # Get expected results
        expected_params = self._get_expected_params(self.materials, many=True)

        # Verify serialized content
        self.assertEqual(response.json(), expected_params)

    def _get_expected_params(self, objects, many=False):
        """Get expected results"""
        if many:
            expected_params = []
            for obj in objects:
                material_obj = get_model_obj_property(Material, obj)
                # JSON serialize Decimal object as string
                material_obj["price"] = str(
                    material_obj["price"].quantize(Decimal("0.01"))
                )
                expected_params.append(material_obj)
            return expected_params

        return get_model_obj_property(Material, obj)
