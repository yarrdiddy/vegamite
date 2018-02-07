import pytest

from pandas import DataFrame, Timestamp

from vegamite.data import MEASUREMENTS

class MockData():
    TRADE_DATA = DataFrame(
        dict(zip(
            ['amount', 'id', 'price', 'timestamp', 'symbol', 'side'],
            [0.01, 34787225, 11143.47, 1517040340806, 'BTC/USD', 'buy']
        )),
        index=[0]
    )

    TREND_DATA = DataFrame(
        dict(zip(
            ['close', 'high', 'low', 'open', 'timestamp', 'volume'],
            [10982.98, 11349, 10850, 11086.88, 1517011200000, 2311.248599]
        )),
        index=[0]
    )

    RAW_OHLCV = [
        [1517961600000, 7691.26, 7819.96, 7215, 7217.44, 2277.4593645299956], 
        [1517875200000, 6905.2, 7948.89, 5873, 7688.46, 19230.629233700616], 
        [1517788800000, 8167.9, 8349.16, 6425.75, 6905.19, 13054.936310890575], 
        [1517702400000, 9227.8, 9350, 7859, 8167.91, 6840.861669600251], 
        [1517616000000, 8785, 9499, 8124.09, 9240, 6838.528816890388], 
        [1517529600000, 9014.22, 9080, 7540, 8787.52, 12129.137117530334], 
        [1517443200000, 10099.99, 10166.25, 8400, 9014.23, 8791.829105850238], 
        [1517356800000, 9995, 10299.95, 9601.02, 10099.99, 5529.0363614902435], 
        [1517270400000, 11123.01, 11150, 9714.84, 9995, 6827.752128190102], 
        [1517184000000, 11536, 11570, 10840, 11123.01, 3993.4809011101333],
    ]


class MockInfluxDB():
    def write_points(self, data, measurement, tags, **kwargs):
        # import ipdb; ipdb.set_trace()
        if not isinstance(data, DataFrame):
            raise ValueError('Influx needs DataFrame for vegamite purposes... Dunno what you just sent in but its no good.')

        if measurement not in MEASUREMENTS:
            raise ValueError("Unsupported measurement being passed to influx. You're going to lose data this way.")

    def query_last_trade(self, query):
        data = MockData.TRADE_DATA
        last_df = DataFrame(data, index=[0])
        return {'trade_data': last_df}

    def query_last_trend(self, query):
        data = MockData.TREND_DATA
        last_df = DataFrame(data, index=[0])
        return {'trade_data': last_df}


class MockExchange():
    def fetch_ohlcv(self, symbol, freq, since=None):
        return MockData.RAW_OHLCV


