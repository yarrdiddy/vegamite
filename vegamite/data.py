import ccxt
import datetime
import redis

from pandas import DataFrame
from influxdb import DataFrameClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from vegamite.config import config

random = 'foo'
DB_CONNECTION = "mysql://{user}:{password}@{host}:{port}/{database}"

def redis_client():
    return redis.Redis(host=config.redis.host, port=config.redis.port, db=config.redis.db)


def get_database_connection():
    engine = create_engine(
        DB_CONNECTION.format(
            database=config.database.name,
            user=config.database.user,
            password=config.database.password,
            host=config.database.host,
            port=config.database.port
        )
    )
    Session = sessionmaker(bind=engine)
    return Session()


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

    def get_last_trade(self, exchange, symbol):
        """
        Return most recently saved trade for an exchange/symbol pair.
        TODO: Fix table naming, still in development.
        """
        last_saved_trade = self.client.query(
            """
            select  last(timestamp) 
            from    test_trade_data 
            where   exchange = '%s' 
            and     symbol = '%s'
            """ % (exchange, symbol)
        )
        return_data = last_saved_trade.get('test_trade_data')
        if return_data is None:
            return_data = DataFrame()
        return return_data

    def get_last_trade_times(exchange):
        """
        Return a dict of most recent saved trade times. Useful for paginating latest trade data.
        """
        last_saved_trades = self.client.query(
            """
            select  symbol, 
                    last(price) 
            from    test_trade_data 
            where   exchange = '%s' 
            group by symbol
            """ % (exchange)
        )
        results = {}
        for i in last_saved_trades.values():
            if len(i) > 0:
                results[i['symbol'].values[0]] = i.index[0]


class MarketData(object):
    """
    Market data class for getting and retrieving market data stored in InfluxDB.
    """

    def __init__(self, exchange_code=None):
        self.exchange = None
        self.exchange_code = exchange_code
        if exchange_code:
            self = self.set_exchange(exchange_code)

    def set_exchange(self, exchange_code):
        self.exchange_code = exchange_code
        self.exchange = eval('ccxt.%s()' % self.exchange_code)
        self.exchange.load_markets()
        return self        
    
    def get_all_exchanges(self, save=False, use_cached=False):
        exchanges = ccxt.exchanges
        return exchanges

    def get_markets(self, save=False, use_cached=False):
        return self.exchange.markets

    def get_trend(self, symbol, resolution='1d', save=False, use_cached=False):
        ohlcv = self.exchange.fetch_ohlcv(symbol, resolution)

        ohlcv_dataframe = DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        ohlcv_dataframe['timestamp'] = (ohlcv_dataframe['timestamp'] / 1000).apply(datetime.datetime.fromtimestamp)
        ohlcv_dataframe = ohlcv_dataframe.set_index('timestamp')

        return ohlcv_dataframe

    def get_trades(self, symbol, since=None):
        trades = self.exchange.fetch_trades(symbol, since=since)
        if len(trades) == 0:
            return DataFrame()
        data_frame = DataFrame(trades, columns=trades[0].keys())
        data_frame['pd_timestamp'] = (data_frame['timestamp'] / 1000).apply(datetime.datetime.fromtimestamp)
        data_frame.index = data_frame['pd_timestamp']
        return data_frame



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