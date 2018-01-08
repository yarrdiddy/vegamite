import ccxt
import datetime

from pandas import DataFrame
from influxdb import DataFrameClient

from vegamite.config import config

random = 'foo'

class TimeSeriesClient(object):
    """
    Time series object for interacting with the InfluxDB instance. Get/retrieve methods for time series data.
    
    TODO: Why do I need to wrap this guy at all? Probably something simpler that just handles the connection.
    """
    def __init__(self):
        self.client = DataFrameClient(
            config.influx.host, 
            config.influx.port, 
            config.influx.user, 
            config.influx.password, 
            config.influx.name
        )
        self.protocol = 'json'

    def write_dataframe(self, dataframe, series, tags=None, field_columns=None, tag_columns=None):
        self.client.write_points(
            dataframe, 
            series,
            tags, 
            protocol=self.protocol,
            field_columns=field_columns,
            tag_columns=tag_columns)


class MarketData(object):
    """
    Market data class for getting and retrieving market data stored in InfluxDB.
    """

    def __init__(self, exchange_code=None):
        self.exchange = None
        self.exchange_code = exchange_code
        if exchange_code:
            self.exchange = eval('ccxt.%s()' % exchange_code)

    def set_exchange(self, exchange_code):
        self.exchange_code = exchange_code
        self.exchange = eval('ccxt.%s()' % self.exchange_code)
        return self        
    
    def get_all_exchanges(self, save=False, use_cached=False):
        exchanges = ccxt.exchanges
        return exchanges

    def get_markets(self, save=False, use_cached=False):
        markets = self.exchange.load_markets()
        return markets

    def get_trend(self, symbol, resolution='1d', save=False, use_cached=False):
        ohlcv = self.exchange.fetch_ohlcv(symbol, resolution)

        ohlcv_dataframe = DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        ohlcv_dataframe['timestamp'] = (ohlcv_dataframe['timestamp'] / 1000).apply(datetime.datetime.fromtimestamp)
        ohlcv_dataframe = ohlcv_dataframe.set_index('timestamp')

        return ohlcv_dataframe




class StaticData(object):
    """
    Static data class for interacting wit hstatic data stored in MySQL.
    """
    pass


class CacheClient(object):
    """
    Object for interacting with the cache.
    """
    pass