import requests
import json

from vegamite.api.GDAX import GDAXClient
from vegamite.config import config

# import ipdb; ipdb.set_trace()
api_base = config.gdax.api_root
api_key = config.gdax.api_key
secret_key = config.gdax.secret_key
passphrase = config.gdax.passphrase


# def test_config():
#     print(config)


# def test_gdax_response():
#     assert len(products(api_base)) > 0


# def test_gdax_request_string():
#     auth = GDAXRequestAuth()


# def test_order():
#     auth = GDAXRequestAuth()
#     order_url = api_base + '/orders'
#     order_data = {
#         'type': 'market',
#         'side': 'sell',
#         'product_id': 'BTC-USD',
#         'size': '0.1'
#     }

#     order_placed_response = requests.post(order_url, data=json.dumps(order_data), auth=auth)
#     order_data = order_placed_response.json()
#     order_id = order_data['id']
#     order_url = api_base + '/orders/' + order_id

#     order_status_response = requests.get(order_url, auth=auth)

#     import ipdb;ipdb.set_trace()
#     print(response.json())