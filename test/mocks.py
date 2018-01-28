import pytest

from pandas import DataFrame, Timestamp

from vegamite.data import MEASUREMENTS

class MockInfluxDB():
    def write_points(self, data, measurement, tags, **kwargs):
        # import ipdb; ipdb.set_trace()
        if not isinstance(data, DataFrame):
            raise ValueError('Influx needs DataFrame for vegamite purposes... Dunno what you just sent in but its no good.')

        if measurement not in MEASUREMENTS.values():
            raise ValueError("Unsupported measurement being passed to influx. You're going to lose data this way.")


    def query_last_trade(self, query):
        data = dict(zip(
            ['last_amount', 'last_id', 'last_price', 'last_timestamp'],
            [0.01, 34787225, 11143.47, 1517040340806]
        ))
        last_df = DataFrame(data, index=[0])
        return {'trade_data': last_df}

    def query_last_trend(self, query):
        data = dict(zip(
            ['last_close', 'last_high', 'last_low', 'last_open', 'last_timestamp', 'last_volume'],
            [10982.98, 11349, 10850, 11086.88, 1517011200000, 2311.248599]
        ))
        last_df = DataFrame(data, index=[0])
        return {'trade_data': last_df}