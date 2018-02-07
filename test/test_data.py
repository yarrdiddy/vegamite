import requests, json, time, pytest, datetime
import numpy as np

# import ipdb; ipdb.set_trace()
from vegamite.config import config
from vegamite.data import MarketData, TimeSeriesClient, redis_client
from vegamite.tasks import queue_tasks, get_exchange_data

from mocks import MockData

import ipdb
api_base = config.gdax.api_root
api_key = config.gdax.api_key
secret_key = config.gdax.secret_key
passphrase = config.gdax.passphrase

test_exchange = 'gdax'
symbol = 'BTC/USD'
r = redis_client()

class MockTSResponse():
    def get_last_query(self, query_string):
        # ipdb.set_trace()
        print('yay!')
        return 'cunt!'

@pytest.fixture()
def mock_get_last_query(monkeypatch):
    monkeypatch.setattr('influxdb.DataFrameClient.query', MockTSResponse.get_last_query)


class TestTimeSeries(object):

    def setup(self):
        self.client = TimeSeriesClient()

    @pytest.mark.usefixtures("mock_write_points")
    def test_write_points(self):
        """
        Test write points, this is achieving very little but forces the code to be run.
        """
        test_data = MockData.TREND_DATA
        self.client.write_dataframe(
            test_data, 
            'trend_data', 
            tags={
                'exchange': test_exchange,
                'symbol': 'BTC/USD',
                'resolution': '1d'
            }, 
            field_columns=['open', 'high', 'low', 'close', 'volume'], 
        )
        # This test will fail in the fixture... it was written to test the test.
        assert True

    @pytest.mark.usefixtures("mock_write_points")
    def test_write_trades(self):
        trades = MockData.TRADE_DATA
        self.client.write_dataframe(
            trades[['symbol', 'side', 'id', 'price', 'amount']],
            'trade_data',
            tags={
                'exchange': 'gdax'
            },
            tag_columns=['symbol', 'side']
        )
        assert True

    @pytest.mark.usefixtures("mock_last_trend")
    def test_get_last(self):
        last_val = self.client.get_last(test_exchange, symbol, 'trend')
        


class TestMarketData(object):

    def setup(self):
        self.exchange = test_exchange
        self.market_data = MarketData(exchange_code=self.exchange)
    
    def test_set_exchange(self):
        new_market_data = self.market_data.set_exchange('bitfinex')
        assert new_market_data.exchange_code == 'bitfinex'
        self.market_data = self.market_data.set_exchange(test_exchange)

    def test_get_all_exchanges(self):
        exchanges = self.market_data.get_all_exchanges()
        time.sleep(1)
        assert len(exchanges) > 0

    def test_get_markets(self):
        markets = self.market_data.get_markets()
        time.sleep(1)
        assert len(markets) > 0

    @pytest.mark.usefixtures("mock_exchange")
    def test_get_trend(self):
        self.market_data = self.market_data.get_trend('BTC/USD', freq='1d', wait=False)

        assert len(self.market_data.result['trend_data'].index) == 10

    def test_get_trades(self):
        # import ipdb; ipdb.set_trace()
        self.market_data = self.market_data.get_trades(symbol)

        self.market_data.save()

    def test_global_lock(self):
        # ipdb.set_trace()
        test_lock = {'id': 12345, 'expire': 0}
        r.set('lock_gdax', json.dumps(test_lock))
        
        # Lock has expired
        self.market_data.lock()

        expire_time = datetime.datetime.now() + datetime.timedelta(1)
        test_lock2 = {'id': 12345, 'expire': expire_time.timestamp()}

        # Lock has not expired, but belongs to market_data
        self.market_data._id = 12345
        self.market_data.release()


    def test_wait(self):
        task1 = '{"task": "trade_data", "symbol": "ETH/EUR"}'
        task2 = '{"task": "trade_data", "symbol": "BTC/USD"}'

        r.delete('gdax-tasks')
        r.lpush('gdax-tasks', task1, task2)

        get_exchange_data('gdax')



# def test_poll_new_trades():
#     poll_new_trades('trade_data')
#     get_exchange_data('gdax')


