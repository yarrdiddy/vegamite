from vegamite.api.GDAX import GDAXClient


gdax_client = GDAXClient()

def test_validate_order():
	gdax_client.validate_order(order_type='limit')


