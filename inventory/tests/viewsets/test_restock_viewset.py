from inventory.tests.viewsets.base import BaseTestCase

from inventory.tests.factories import StoreFactory, MaterialStockFactory
from inventory.models import Material, MaterialStock


class RestockViewSetTestCases(BaseTestCase):
    """Testing the Restock ViewSet with GET and POST method, which include
       serialized format, total_price and update of current_capacity (>= 0 && <= max_capacity"""

    def setUp(self):
        """Create restock data"""
        super().setUp()
        store = StoreFactory(user=self.user)
        self.data = MaterialStockFactory.create_batch(
            3,
            store=store,
            current_capacity=10,
            max_capacity=100
        )

    def test_get_restock(self):
        """Verify that the material stock and the total price are correctly serialized"""
        response = self.client.get(
            '/api/v1/restock/',
            HTTP_AUTHORIZATION=self.formatted_token
        )

        # Access allow
        self.assertEqual(response.status_code, 200)

        # Get expected results
        expected_params = self._get_expected_params(self.data)

        # Verify expected results
        self.assertEqual(response.json(), expected_params)

    def test_post_restock(self):
        """Verify that update of the stock quantity with valid data"""

        post_data = {
            "materials": self._modify_data_quantity(),
        }

        response = self.client.post(
            '/api/v1/restock/',
            data=post_data,
            format='json',
            HTTP_AUTHORIZATION=self.formatted_token
        )

        # Verify access
        self.assertEqual(response.status_code, 200)

        # Get objects from database
        updated_objects = MaterialStock.objects.filter(pk__lte=3)

        # Get expected results
        expected_params = self._get_expected_params(updated_objects)

        # Verify response content
        self.assertEqual(response.json(), expected_params)

        # Verify database update
        for updated_obj in updated_objects:
            # Make sure that the capacity is updated correctly
            self.assertEqual(updated_obj.max_capacity, 100)
            self.assertEqual(updated_obj.current_capacity, 60)

    def test_post_restock_exceed(self):
        """Verify that stock quantity does not update when current capacity > max_capacity"""

        # current_capacity (10 + 91) > max_capacity (100)
        post_data = {
            "materials": self._modify_data_quantity(91),
        }

        response = self.client.post(
            '/api/v1/restock/',
            data=post_data,
            format='json',
            HTTP_AUTHORIZATION=self.formatted_token
        )

        # Verify bad request
        self.assertEqual(response.status_code, 400)

    def test_post_restock_negative(self):
        """Verify that stock quantity does not update when current capacity < 0"""

        # current_capacity < 0
        post_data = {
            "materials": self._modify_data_quantity(-11),
        }

        response = self.client.post(
            '/api/v1/restock/',
            data=post_data,
            format='json',
            HTTP_AUTHORIZATION=self.formatted_token
        )

        # Verify bad request
        self.assertEqual(response.status_code, 400)

    def _modify_data_quantity(self, quantity=50):
        """Modify the current capacity of the MaterialStock object"""
        array = []
        for dt in self.data:
            array.append({
                "material": dt.material.material_id,
                "quantity": quantity
            })
        return array

    def _get_expected_params(self, objects):
        """Get expected results"""
        materials = []
        for obj in objects:
            materials.append(self._get_expected_obj(obj))

        total_price = 0
        for material in materials:
            if "material" in material or "quantity" in material:
                try:
                    price = Material.objects.get(
                        pk=material.get('material')
                    ).price
                    total_price += price * material.get('quantity')
                except Material.DoesNotExist:
                    raise ValueError("material is not found.")

        expected_params = {
            "materials": materials,
            "total_price": float(round(total_price, 2))
        }
        return expected_params

    def _get_expected_obj(self, obj):
        """Change foreign key from model obj to pk"""
        expected_obj = {
            "material": obj.material.pk,
            "quantity": obj.max_capacity - obj.current_capacity
        }
        return expected_obj
