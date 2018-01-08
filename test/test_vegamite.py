import requests
import json

# import ipdb; ipdb.set_trace()
from vegamite.config import config
from vegamite.data import MarketData, TimeSeriesClient

import ipdb
api_base = config.gdax.api_root
api_key = config.gdax.api_key
secret_key = config.gdax.secret_key
passphrase = config.gdax.passphrase

test_exchange = 'gdax'


class TestTimeSeries(object):

    def setup(self):
        self.client = TimeSeriesClient()
        self.exchange = MarketData(exchange_code=test_exchange)

    def test_write_points(self):
        ipdb.set_trace()
        test_data = self.exchange.get_trend('BTC/USD', '1d')
        self.client.write_dataframe(
            test_data, 
            'test_data', 
            tags={
                'exchange': test_exchange,
                'symbol': 'BTC/USD',
                'resolution': '1d'
            }, 
            field_columns=['open', 'high', 'low', 'close', 'volume'], 
        )

        result = self.client.query('select * from test_data')
        assert len(result['test_data']) > 0


class TestMarketData(object):

    def setup(self):
        self.exchange = test_exchange
        self.market_data = MarketData(exchange_code=self.exchange)
    
    def test_set_exchange(self):
        # import ipdb; ipdb.set_trace()
        new_market_data = self.market_data.set_exchange('_1broker')
        assert new_market_data.exchange_code == '_1broker'
        self.market_data = self.market_data.set_exchange(test_exchange)

    def test_get_all_exchanges(self):
        exchanges = self.market_data.get_all_exchanges()
        assert len(exchanges) > 0

    def test_get_markets(self):
        markets = self.market_data.get_markets()
        assert len(markets) > 0

    def test_get_trend(self):
        ohlcv = self.market_data.get_trend('BTC/USD', '1d')
        assert len(ohlcv) > 0
        assert ohlcv.index.dtype == 'datetime64[ns]'


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