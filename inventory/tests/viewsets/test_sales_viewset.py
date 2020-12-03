from inventory.tests.viewsets.base import BaseTestCase

from inventory.tests.factories import StoreFactory, MaterialStockFactory, ProductFactory, MaterialQuantityFactory
from inventory.models import MaterialStock
from inventory.services.product import get_product_remaining_capacities


class SalesTestCases(BaseTestCase):
    """Test the Sales ViewSet with POST method, which include
       testing validity to sell the products in the store."""

    def setUp(self):
        """Create restock data"""
        super().setUp()
        # Create products
        product1 = ProductFactory()
        product2 = ProductFactory()
        product3 = ProductFactory()
        # create Store
        self.store = StoreFactory.create(
            user=self.user,
            products=(product1, product2, product3,)
        )
        # Create material
        material_stock = MaterialStockFactory(
            store=self.store,
            current_capacity=100
        )

        # Link material with products
        MaterialQuantityFactory(
            product=product1,
            ingredient=material_stock.material,
            quantity=10
        )
        MaterialQuantityFactory(
            product=product2,
            ingredient=material_stock.material,
            quantity=10
        )
        MaterialQuantityFactory(
            product=product3,
            ingredient=material_stock.material,
            quantity=10
        )

        self.data = {
            "sale": [
                {
                    "product": product1.product_id,
                    "quantity": 1,
                },
                {
                    "product": product2.product_id,
                    "quantity": 2,
                },
                {
                    "product": product3.product_id,
                    "quantity": 3,
                },
            ]
        }
        self.invalid_data = {
            "sale": [
                {
                    "product": product1.product_id,
                    "quantity": 100,
                },
            ]
        }

    def test_sold_product_valid(self):
        """Verify selling of product without running out of material"""
        response = self.client.post(
            '/api/v1/sales/',
            data=self.data,
            format='json',
            HTTP_AUTHORIZATION=self.formatted_token
        )

        # Verify access allow
        self.assertEqual(response.status_code, 200)

        # Verify the sales content
        self.assertEqual(response.json(), self._get_expected_params())

        material_stock = MaterialStock.objects.last()

        # Verify the current capacity of the ingredient is updated correctly
        # remaining capacity: 100 - 10 - 20 - 30 = 40
        self.assertEqual(material_stock.current_capacity, 40)

    def test_sold_product_out_of_material(self):
        """Verify do not sell product than ran out of material"""
        response = self.client.post(
            '/api/v1/sales/',
            data=self.invalid_data,
            format='json',
            HTTP_AUTHORIZATION=self.formatted_token
        )

        # Verify operation denial
        self.assertEqual(response.status_code, 400)

    def _get_expected_params(self):
        """Get expected results"""
        return {
            # quantity = remaining product capacity, (100-10-20-30)/10 = 4
            "sale": [
                {
                    "product": 1,
                    "quantity": 4,
                },
                {
                    "product": 2,
                    "quantity": 4,
                },
                {
                    "product": 3,
                    "quantity": 4,
                },
            ]
        }
