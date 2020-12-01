from inventory.tests.viewsets.base import BaseTestCase

from inventory.tests.factories import StoreFactory, MaterialStockFactory, ProductFactory, MaterialQuantityFactory
from inventory.serializers import ProductCapacitySerializer


class ProductCapacityTestCases(BaseTestCase):
    """Test the Product Capacity ViewSet with GET method, which include
       testing the remaining capacities for each products in the store."""

    def setUp(self):
        """Create restock data"""
        super().setUp()
        # Create product
        product1 = ProductFactory()
        product2 = ProductFactory()
        # create Store
        self.store = StoreFactory.create(
            user=self.user, products=(product1, product2))
        # Create material
        ms1 = MaterialStockFactory(store=self.store, current_capacity=30)
        ms2 = MaterialStockFactory(store=self.store, current_capacity=40)
        ms3 = MaterialStockFactory(store=self.store, current_capacity=50)
        # Link material with product
        MaterialQuantityFactory(
            quantity=6, product=product1, ingredient=ms1.material)
        MaterialQuantityFactory(
            quantity=7, product=product1, ingredient=ms2.material)
        MaterialQuantityFactory(
            quantity=5, product=product2, ingredient=ms2.material)
        MaterialQuantityFactory(
            quantity=10, product=product2, ingredient=ms3.material)

    def test_get_product_capacity(self):
        """Verify the format and the remaining capacity for each products in the store"""
        response = self.client.get('/api/v1/product-capacity/',
                                   HTTP_AUTHORIZATION=self.formatted_token)

        # Verify access allow
        self.assertEqual(response.status_code, 200)

        # Get expected results
        expected_params = ProductCapacitySerializer(instance=self.store).data,

        self.assertEqual(response.json(), expected_params)

        # Verify the calculation for remaining capacity (rc)
        expected_rc_p1 = min([int(30/6), int(40/7)])
        received_rc_p1 = response.json()["remaining_capacities"][0]["quantity"]
        self.assertEqual(expected_rc_p1, received_rc_p1)

        # Verify second rc, make sure that overlapping of material with product1
        # does not affect the rc of product 2
        expected_rc_p2 = min([int(40/5), int(50/10)])
        received_rc_p2 = response.json()["remaining_capacities"][1]["quantity"]
        self.assertEqual(expected_rc_p2, received_rc_p2)
