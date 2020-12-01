from inventory.tests.viewsets.base import BaseTestCase

from inventory.tests.factories import StoreFactory, MaterialStockFactory, ProductFactory, MaterialQuantityFactory


class SalesTestCases(BaseTestCase):
    """Test the Sales ViewSet with POST method, which include
       testing validity to sell the products in the store."""

    def setUp(self):
        """Create restock data"""
        super().setUp()
        # Create product
        product = ProductFactory()
        # create Store
        store = StoreFactory.create(
            user=self.user, products=(product,))
        # Create material
        material_stock = MaterialStockFactory(store=store)

        # Link material with product
        MaterialQuantityFactory(
            product=product, ingredient=material_stock.material)

        self.data = {
            "sale":
            [
                {
                    "product": product.product_id,
                    "quantity": 1,
                },
            ]
        }
        self.invalid_data = {
            "sale":
            [
                {
                    "product": product.product_id,
                    "quantity": 1,
                },
            ]
        }

    def test_sold_product_valid(self):
        """Verify selling of product without running out of material"""
        response = self.client.post('/api/v1/sales/', data=self.data, format='json',
                                    HTTP_AUTHORIZATION=self.formatted_token)

        # Verify access allow
        self.assertEqual(response.status_code, 200)

        # TODO: Update sale
        # sale = SalesSerializer(self.store).data
        expected_params = {
            "sale": [],
        }
        # Verify the sales content
        self.assertEqual(response.json(), expected_params)

    def test_sold_product_out_of_material(self):
        """Verify do not sell product than ran out of material"""
        response = self.client.post('/api/v1/sales/', data=self.invalid_data, format='json',
                                    HTTP_AUTHORIZATION=self.formatted_token)

        # Verify operation denial
        self.assertEqual(response.status_code, 400)

        # TODO: Update sale
        # sale = SalesSerializer(self.store).data
        expected_params = {
            "sale": [],
        }
        # Verify that the sales does not update
        self.assertEqual(response.json(), expected_params)
