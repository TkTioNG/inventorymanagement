from inventory.tests.test_viewsets import BaseTestCase

from inventory.tests.factories import StoreFactory, MaterialStockFactory


class InventoryTestCases(BaseTestCase):
    """Test the Inventory ViewSet with GET method, which include
       testing of serialized format, and the percentage of capacity."""

    def setUp(self):
        """Create restock data"""
        super().setUp()
        store = StoreFactory(user=self.user)
        self.data = MaterialStockFactory.create_batch(
            3, store=store, current_capacity=60, max_capacity=90)

    def test_get_inventory(self):
        """Verify the serialized format and the percentage_of_capacity"""
        # percentage_of_capacity = decimal (XX.XX)
        response = self.client.get('/api/v1/inventory/',
                                   HTTP_AUTHORIZATION=self.formatted_token)

        # Verify access allowed
        self.assertEqual(response.status_code, 200)

        # TODO: Update materials
        # material = InventorySerializer(instance=self.data, many=True).data
        expected_params = {
            "materials": [],
        }
        # Verify serialized content
        self.assertEqual(response.json(), expected_params)

        received_poc = response.json().materials[0]["percentage_of_capacity"]
        expected_poc = 66.67  # round(60/90, 2), 2 d.p.
        # Verify decimal points of percentage_of_capacity
        self.addClassCleanup(received_poc, expected_poc)
