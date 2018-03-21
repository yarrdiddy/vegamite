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


def test_trades():
    bn = MarketData('binance')
    gd = MarketData('gdax')

    bn = bn.get_trades('ETH/BTC')
    gd = gd.get_trades('BTC/USD')

    bn = bn.save(retention_policy="90day") # 
    gd = gd.save(retention_policy="90day")

    # bn = bn.save()
    # gd = gd.save()


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

    # @pytest.mark.usefixtures("mock_exchange")
    def test_get_trend(self):
        self.market_data = self.market_data.get_trend('BTC/USD', freq='5m', wait=False)
        assert len(self.market_data.result['trend_data'].index) == 10

    @pytest.mark.usefixtures("mock_exchange")
    def test_get_trades(self):
        self.market_data = self.market_data.get_trades('BTC/USD', wait=False)
        assert len(self.market_data.result['trade_data'].index) == 3

    def test_global_lock(self):
        # TODO: this test depends on redis... mock?
        md1 = MarketData('gdax')
        md2 = MarketData('gdax')

        # Check they have different id's
        assert md1._id != md2._id

        # Test manually locking
        md1.lock()
        with pytest.raises(Exception) as e_info:
            md2.lock()

        md1.release()
        # Ensure I can release the lock
        assert md1._check_lock() is None

        # Test locking via context handler
        with md1 as _md1:
            with pytest.raises(Exception) as e_info:
                md2.lock()

        # Ensure context handler released cleanly
        assert md1._check_lock() is None

    @pytest.mark.usefixtures("mock_exchange")
    def test_save(self):
        self.market_data.result.clear()

        self.market_data = self.market_data.get_trend('BTC/USD', freq='1d', wait=False)
        self.market_data = self.market_data.get_trades('BTC/USD', wait=False)

        self.market_data.save()

        assert self.market_data.result == {}


