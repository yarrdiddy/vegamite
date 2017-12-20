import requests, base64, hashlib, hmac, time

from requests.auth import AuthBase
from vegamite.config import config


class GDAXRequestAuth(AuthBase):

    def __init__(self):
        self.api_key = config.gdax.api_key
        self.secret_key = config.gdax.secret_key
        self.passphrase = config.gdax.passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode('utf-8'), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())
        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request


def order_market(direction, product_id, size):
    auth = GDAXRequestAuth()
    order_url = api_base + '/orders'
    order_data = {
        'type': 'market',
        'side': direction,
        'product_id': product_id,
        'size': str(size)
    }

    order_placed_response = requests.post(order_url, data=json.dumps(order_data), auth=auth)
    order_data = order_placed_response.json()

    return order_data['id']


def order_limit(direction, product_id, price, size, time_in_force='BTC', cancel_after=None, post_only=None):
    auth = GDAXRequestAuth()

    order_data = {
        'type': 'limit',
        'side': direction,
        'product_id': product_id,
        'price': price,
        'size': size,
        'time_in_force': time_in_force
    }

    if time_in_force == 'GTT':
        order_data['cancel_after'] = cancel_after
    if time_in_force not in ['IOC', 'FOK']:
        order_data['post_only'] = post_only

    order_placed_response = requests.post(order_url, data=json.dumps(order_data), auth=auth)
    if response.status_code is not 200:
        raise Exception('Invalid GDAX Status Code: %d' % response.status_code)
    
    order_data = order_placed_response.json()


def order_status(order_id):
    order_url = config.api_base + '/orders/' + order_id
    order_status_response = requests.get(order_url, auth=auth)

    return order_status_response.json()


def products(api_base):
    response = requests.get(api_base + '/products')

    # Check for invalid response
    if response.status_code is not 200:
        raise Exception('Invalid GDAX Status Code: %d' % response.status_code)

    return response.json()