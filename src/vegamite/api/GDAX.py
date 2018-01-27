import requests, base64, hashlib, hmac, time, json

from requests.auth import AuthBase
from vegamite.config import config


class GDAXAuth(AuthBase):

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


class GDAXClient(object):

    ORDER_TYPES=['limit', 'market', 'stop']
    TIME_IN_FORCE=['GTC', 'GTT', 'IOC', 'FOK']


    def __init__(self):
        self.api_root = config.gdax.api_root
        self.auth = GDAXAuth()

    # Maybe refactor these out? Maybe conbine them
    def _get_request(self, request_path, order_data=None):
        try:
            response = requests.get(request_path, auth=self.auth, timeout=30)
        except requests.exceptions.Timeout:
            # Log the exception
            print(e)
            return None
        except requests.exceptions.TooManyRedirects:
            # Log the exception
            print(e)
            return None
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            print(e)
            return None
        return response

    def _post_request(self, request_path, order_data):
        # import ipdb; ipdb.set_trace()
        try: 
            response = requests.post(request_path, data=order_data, auth=self.auth, timeout=30)
        except requests.exceptions.Timeout:
            # Log the exception
            print(e)
            return None
        except requests.exceptions.TooManyRedirects:
            # Log the exception
            print(e)
            return None
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            print(e)
            return None
        return response

    def validate_order(self, **kwargs):
        order_type = kwargs.get('order_type')   # Market/Limit/Stop
        time_in_force = kwargs.get('time_in_force')
        # import ipdb;ipdb.set_trace()
        if order_type is not None and order_type not in GDAXClient.ORDER_TYPES:
            raise ValueError('Invalid order type: %s. Should be one of: limit, market, or stop' %order_type)

        if time_in_force is not None and time_in_force not in GDAXClient.TIME_IN_FORCE:
            raise ValueError('Invalid time_in_force code: %s. Should be one of: GTC, GTT, IOC, or FOK' %time_in_force)

        product_id = kwargs.get('product_id', None)

        # One of size or funds is needed
        size = kwargs.get('size')
        funds = kwargs.get('funds') 
        
        if order_type == 'STOP':
            stop_price = kwargs.get('stop_price')

        if product_id is None:
            # Raise an exception here, please don't order nothing, and a default is dumb
            raise ValueError('No product_id supplied.')

    def get_account_list(self):
        request_path = self.api_root + '/accounts'
        return self._get_request(request_path)

    def get_account(self, account_id):
        request_path = self.api_root + '/accounts/' + account_id
        return self._get_request(request_path)

    def get_account_history(self, account_id):
        request_path = self.api_root + '/accounts/' + account_id + '/ledger'
        return self._get_request(request_path)

    def get_holds(self, account_id):
        request_path = self.api_root + '/accounts/' + account_id + '/holds'
        return self._get_request(request_path)

    def buy(self, **kwargs):
        # import ipdb;ipdb.set_trace()
        kwargs['side'] = 'buy'
        try:
            self.validate_order(**kwargs)
        except:
            # Log something
            return None
        request_path = self.api_root + '/orders'
        order_data = json.dumps(kwargs)

        return self._post_request(request_path, order_data)


    def sell(self, **kwargs):
        kwargs['side'] = 'sell'
        self.validate_order(kwargs)
        request_path = self.api_root + '/orders'
        order_data = json.dumps(kwargs)

        return _post_request(request_path, order_data)

    def cancel_order(self, order_id):
        pass

    def cancel_all_orders(self):
        pass

    def get_orders(self):
        pass

    def get_order(self, order_id):
        pass

    def get_fills(self):
        # Need to figure out pagination stuff
        pass

    def get_positions(self):
        pass

    def get_reports(self):
        pass

    def get_report(self, report_id):
        pass

    def get_trailing_volume(self):
        pass




def send_request(gdax_request, order_data={}):
    
    # Need an order_url, order_data, and auth object
    # Also need to determine the method
    api_root = config.gdax.api_root
    auth = GDAXAuth()
    request_args = GDAXRequests.get(gdax_request)
    order_url = api_root + request_args['path']
    request_type = request_args['type']

    if not isinstance(order_data, dict):
        # TODO: Raise an exception here
        return {}
    else:
        order_data = json.dumps(order_data)

    if request_type == 'POST':
        response = requests.post(order_url, data=request_data, auth=auth)
    elif request_type == 'GET':
        response = requests.get(order_url, auth=auth)

    return response



def order_market(direction, product_id, size):
    auth = GDAXAuth()
    order_url = api_root + '/orders'
    order_data = {
        'type': 'market',
        'side': direction,
        'product_id': product_id,
        'size': str(size)
    }

    order_response = send_request('ORDERS', order_data)

    return order_response.json()


def order_limit(direction, product_id, price, size, time_in_force='BTC', cancel_after=None, post_only=None):
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

    order_response = send_request('ORDERS', order_data)
    if response.status_code is not 200:
        raise Exception('Invalid GDAX Status Code: %d' % response.status_code)
    
    return order_response.json()


def order_status(order_id):
    order_url = config.api_root + GDAXRequests['ORDERS']['path'] + order_id
    order_status_response = requests.get(order_url, auth=auth)

    return order_status_response.json()


def products(api_root):
    import ipdb; ipdb.set_trace()
    response = requests.get(api_root + '/products')

    # Check for invalid response
    if response.status_code is not 200:
        raise Exception('Invalid GDAX Status Code: %d' % response.status_code)

    return response.json()

