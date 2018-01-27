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

MEASUREMENTS = ['trade_data', 'trend_data']

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

    def get_last(self, exchange, symbol, measurement):
        """
        Return most recently saved trade for an exchange/symbol pair.
        TODO: Fix table naming, still in development.
        """
        last_saved = self.client.query(
            """
            select  last(*) 
            from    %s 
            where   exchange = '%s' 
            and     symbol = '%s'
            """ % (measurement, exchange, symbol)
        )
        return_data = last_saved.get(self.trade_data_table)
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

        self.result = {}

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

    def get_trend(self, symbol, freq='1d', since=None, latest=True):

        last_timestamp = 0
        
        if latest:
            last_saved = self.ts_client.get_last(self.exchange_code, symbol, 'trade_data')

            if len(last_saved.index) > 0:
                last_timestamp = int(last_saved['last_timestamp'])

        ohlcv = self.exchange.fetch_ohlcv(symbol, freq, since=last_timestamp)
        if len(ohlcv) == 0:
            return self

        ohlcv_dataframe = DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        ohlcv_dataframe['pd_timestamp'] = (ohlcv_dataframe['timestamp'] / 1000).apply(datetime.datetime.fromtimestamp)
        ohlcv_dataframe['symbol'] = symbol
        ohlcv_dataframe['freq'] = freq
        ohlcv_dataframe = ohlcv_dataframe.set_index('pd_timestamp')

        self.result['trend_data'] = ohlcv_dataframe
        logger.debug('Fetched %s trend: %s, %s.' % (len(data_frame.index), self.exchange_code, symbol))
        return self

    def get_trades(self, symbol, since=None, latest=True):
        # import ipdb; ipdb.set_trace()
        last_timestamp = 0
        
        if latest:
            last_saved = self.ts_client.get_last(self.exchange_code, symbol, 'trade_data')

            if len(last_saved.index) > 0:
                last_timestamp = int(last_saved['last_timestamp'])

        trades = self.exchange.fetch_trades(symbol, since=last_timestamp)
        if len(trades) == 0:
            return self
        data_frame = DataFrame(trades, columns=trades[0].keys())
        data_frame['pd_timestamp'] = (data_frame['timestamp'] / 1000).apply(datetime.datetime.fromtimestamp)
        data_frame.index = data_frame['pd_timestamp']

        self.result['trade_data'] = data_frame
        logger.debug('Fetched %s trades: %s, %s.' % (len(data_frame.index), self.exchange_code, symbol))
        return self


    def save(self):

        _fields = {
            'trade_data': ['id', 'price', 'amount', 'timestamp'],
            'trend_data': ['timestamp', 'open', 'high', 'low', 'close', 'volume'] ##
        }

        _tags = {
            'trade_data': ['symbol', 'side'],
            'trend_data': ['symbol', 'freq']
        }
        
        for result_name, result_data in self.result.items():
            self.ts_client.write_dataframe(
                result_data[_fields[result_name] + _tags[result_name]],
                result_name,
                tags={
                    'exchange': self.exchange_code
                },
                tag_columns=_tags[result_name]
            )

        self.result.clear()
        return self



