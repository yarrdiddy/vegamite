import ccxt
import datetime
import redis
import time

from pandas import DataFrame
from influxdb import DataFrameClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from celery.utils.log import get_task_logger

from vegamite.config import config

random = 'foo'
DB_CONNECTION = "mysql://{user}:{password}@{host}:{port}/{database}"

logger = get_task_logger(__name__)

class Singleton(type):
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance


class Database(metaclass=Singleton):
    def __init__(self):
        self.engine = create_engine(
            DB_CONNECTION.format(
                database=config.database.name,
                user=config.database.user,
                password=config.database.password,
                host=config.database.host,
                port=config.database.port
            )
        )
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()


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


class TimeSeriesClient(metaclass=Singleton):
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
        self.trade_data_table = 'trade_data'

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
            from    %s 
            where   exchange = '%s' 
            and     symbol = '%s'
            """ % (self.trade_data_table, exchange, symbol)
        )
        return_data = last_saved_trade.get(self.trade_data_table)
        if return_data is None:
            return_data = DataFrame()
        return return_data

    def get_last_trade_times(self, exchange):
        """
        Return a dict of most recent saved trade times. Useful for paginating latest trade data.
        """
        last_saved_trades = self.client.query(
            """
            select  symbol, 
                    last(price) 
            from    %s 
            where   exchange = '%s' 
            group by symbol
            """ % (self.trade_data_table, exchange)
        )
        results = {}
        for i in last_saved_trades.values():
            if len(i) > 0:
                results[i['symbol'].values[0]] = i.index[0]


class MarketData(object):
    """
    Market data class for getting and retrieving market data.
    """

    def __init__(self, exchange_code=None):
        self.exchange = None
        self.exchange_code = exchange_code
        if exchange_code:
            self = self.set_exchange(exchange_code)
        self.redis_client = redis_client()
        self.ts_client = TimeSeriesClient()

    def __enter__(self):
        self.redis_client.set('lock_%s' % self.exchange_code, 'true')
        return self

    def __exit__(self, exc_ty, exc_val, tb):
        time.sleep(self.exchange.rateLimit / 1000)
        self.redis_client.set('lock_%s' % self.exchange_code, 'false')

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

    def latest_trades(self, exchange, symbol):
        """
        Given and exchange, poll the market data for the given symbol and save it in InfluxDB.
        """
        market_data = MarketData(exchange)
        ts_client = TimeSeriesClient()

        last_saved_trade = ts_client.get_last_trade(exchange, symbol)
        last_timestamp = 0

        if len(last_saved_trade.index) > 0:
            last_timestamp = int(last_saved_trade['last'])

        return market_data.get_trades(symbol, since=last_timestamp)

    def save_latest_trades(self, symbol):
        trades = self.latest_trades(self.exchange_code, symbol)

        if len(trades.index) == 0:
            logger.debug('No new trades for %s' % (symbol))
        else:
            self.ts_client.write_dataframe(
                trades[['symbol', 'side', 'id', 'price', 'amount', 'timestamp']],
                ts_client.trade_data_table,
                tags={
                    'exchange': self.exchange_code
                },
                tag_columns=['symbol', 'side']
            )
            logger.debug('Wrote %s trades for %s' % (len(trades.index), symbol))

