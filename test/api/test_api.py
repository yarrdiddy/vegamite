import pytest, requests, json, re

from vegamite.api.GDAX import GDAXClient

gdax_client = GDAXClient()


class MockData:
    ACCOUNT_LIST = [
        {
            "id": "71452118-efc7-4cc4-8780-a5e22d4baa53",
            "currency": "BTC",
            "balance": "0.0000000000000000",
            "available": "0.0000000000000000",
            "hold": "0.0000000000000000",
            "profile_id": "75da88c5-05bf-4f54-bc85-5c775bd68254"
        },
        {
            "id": "e316cb9a-0808-4fd7-8914-97829c1925de",
            "currency": "USD",
            "balance": "80.2301373066930000",
            "available": "79.2266348066930000",
            "hold": "1.0035025000000000",
            "profile_id": "75da88c5-05bf-4f54-bc85-5c775bd68254"
        }
    ]

    ACCOUNT_HISTORY = [
        {
            "id": "100",
            "created_at": "2014-11-07T08:19:27.028459Z",
            "amount": "0.001",
            "balance": "239.669",
            "type": "fee",
            "details": {
                "order_id": "d50ec984-77a8-460a-b958-66f114b0de9b",
                "trade_id": "74",
                "product_id": "BTC-USD"
            }
        }
    ]

    HOLDS = [
        {
            "id": "82dcd140-c3c7-4507-8de4-2c529cd1a28f",
            "account_id": "e0b3f39a-183d-453e-b754-0c13e5bab0b3",
            "created_at": "2014-11-06T10:34:47.123456Z",
            "updated_at": "2014-11-06T10:40:47.123456Z",
            "amount": "4.23",
            "type": "order",
            "ref": "0a205de4-dd35-4370-a285-fe8fc375a273",
        }
    ]

    NEW_ORDER_RESPONSE = {
        "id": "d0c5340b-6d6c-49d9-b567-48c4bfca13d2",
        "price": "0.10000000",
        "size": "0.01000000",
        "product_id": "BTC-USD",
        "side": "buy",
        "stp": "dc",
        "type": "limit",
        "time_in_force": "GTC",
        "post_only": False,
        "created_at": "2016-12-08T20:02:28.53864Z",
        "fill_fees": "0.0000000000000000",
        "filled_size": "0.00000000",
        "executed_value": "0.0000000000000000",
        "status": "pending",
        "settled": False
    }

    SELL_ORDER_RESPONSE = {
        "id": "d0c5340b-6d6c-49d9-b567-48c4bfca13d2",
        "price": "0.10000000",
        "size": "0.01000000",
        "product_id": "BTC-USD",
        "side": "sell",
        "stp": "dc",
        "type": "limit",
        "time_in_force": "GTC",
        "post_only": False,
        "created_at": "2016-12-08T20:02:28.53864Z",
        "fill_fees": "0.0000000000000000",
        "filled_size": "0.00000000",
        "executed_value": "0.0000000000000000",
        "status": "pending",
        "settled": False
    }

    def encode_data(data):
        return json.dumps(data).encode('utf-8')

    def get(url, params=None, **kwargs):
        
        response = requests.Response()
        # import ipdb; ipdb.set_trace()

        if re.search(r"/accounts\Z", url):
            response._content = json.dumps(MockData.ACCOUNT_LIST).encode('utf-8')
        elif re.search(r'/accounts/.+/ledger\Z', url):
            response._content = json.dumps(MockData.ACCOUNT_HISTORY).encode('utf-8')
        elif re.search(r'/accounts/.+/holds\Z', url):
            response._content = json.dumps(MockData.HOLDS).encode('utf-8')
        elif re.search(r'/accounts/.+\Z', url):
            account_id = url.split('/')[-1]
            content = {}
            for account in MockData.ACCOUNT_LIST:
                if account['id'] == account_id:
                    content = account
            response._content = json.dumps(content).encode('utf-8')

        return response

    def post(url, data=None, **kwargs):
        # import ipdb; ipdb.set_trace()
        response = requests.Response()
        data_dictionary = json.loads(data)
        if re.search(r'/orders\Z', url) and data is not None:
            if data_dictionary.get('side') == 'buy':
                content = MockData.NEW_ORDER_RESPONSE
            elif data_dictionary.get('side') == 'sell':
                content = MockData.SELL_ORDER_RESPONSE

            response._content = json.dumps(content).encode('utf-8')

        return response






def test_validate_order():
    # Test the invalid orders
    with pytest.raises(ValueError):
        gdax_client.validate_order(order_type='invalid_order_type')
        gdax_client.validate_order(time_in_force='ASDF')

    # Test some valid orders
    gdax_client.validate_order(
        order_type='market',
        product_id='BTC-USD',
        size='0.01'
    )


@pytest.fixture(autouse=True)
def mock_request(monkeypatch):
    monkeypatch.setattr('requests.get', MockData.get)
    monkeypatch.setattr('requests.post', MockData.post)

def test_get_accounts():
    response = gdax_client.get_account_list()
    response_content = response.json()
    assert len(response_content) == 2

def test_get_account():
    account = '71452118-efc7-4cc4-8780-a5e22d4baa53'
    response = gdax_client.get_account(account)
    response_content = response.json()

    assert response_content['id'] == account

def test_get_account_history():
    response = gdax_client.get_account_history('100')
    response_content = response.json()

    assert len(response_content) == 1

def test_buy():
    buy_order = {
        "size": "0.01",
        "price": "0.100",
        "product_id": "BTC-USD"
    }
    response = gdax_client.buy(**buy_order)
    response_content = response.json()

    assert response_content['id'] == 'd0c5340b-6d6c-49d9-b567-48c4bfca13d2'
    assert response_content['side'] == 'buy'


def test_sell():
    buy_order = {
        "size": "0.01",
        "price": "0.100",
        "product_id": "BTC-USD"
    }
    response = gdax_client.buy(**buy_order)
    response_content = response.json()

    assert response_content['id'] == 'd0c5340b-6d6c-49d9-b567-48c4bfca13d2'
    assert response_content['side'] == 'sell'


def test_sell():
    pass

def test_cancel_order():
    pass

def test_cancel_all_orders():
    pass

def test_get_orders():
    pass

def test_get_order():
    pass

def test_get_fills():
    # Need to figure out pagination stuff
    pass

def test_get_positions():
    pass

def test_get_reports():
    pass

def test_get_report():
    pass

def test_get_trailing_volume():
    pass





