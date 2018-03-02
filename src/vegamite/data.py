import ccxt, datetime, redis, time, random, sys, datetime, json

from pandas import DataFrame
from influxdb import DataFrameClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from celery.utils.log import get_task_logger

from vegamite.config import config

DB_CONNECTION = "mysql://{user}:{password}@{host}:{port}/{database}"

MEASUREMENTS = ['trade_data', 'trend_data']

logger = get_task_logger(__name__)

# TODO: Put this into a base module
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
        logger.debug('Wrote %s points to InfluxDB' % len(dataframe.index))
        self.client.write_points(
            dataframe, 
            series,
            tags, 
            protocol=self.protocol,
            field_columns=field_columns,
            tag_columns=tag_columns)

    def get_last(self, exchange, symbol, measurement, **kwargs):
        """
        Return most recently saved data point.
        """
        _extra_filters = kwargs.get('extra_filters')
        _extra_sql = ''
        if _extra_filters:
            for key, val in _extra_filters.items():
                _extra_sql += "and %s = '%s'" % (key, val)

        query_parameters = dict(
            measurement=measurement,
            exchange=exchange,
            symbol=symbol,
            extra_filters=_extra_sql
        )
        last_saved = self.client.query(
            """
            select  last(*) 
            from    %(measurement)s 
            where   exchange = '%(exchange)s' 
            and     symbol = '%(symbol)s'
            %(extra_filters)s
            """ % query_parameters
        )
        return_data = last_saved.get(measurement)
        if return_data is None:
            return_data = DataFrame()
        return return_data


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

        self._id = random.getrandbits(128)

    def __enter__(self):
        # print('Entering... ID = %s' % self._id)
        self.lock()
        return self

    def __exit__(self, exc_ty, exc_val, tb):
        # print('Exiting...')
        self.release()

    # TODO: Refactor lock out into its own class
    def _check_lock(self):
        # import ipdb; ipdb.set_trace()
        current_lock = self.redis_client.get('lock_%s' % self.exchange_code)
        time_check = datetime.datetime.now()
        time_check = time_check.timestamp()
        if current_lock:
            lock_params = json.loads(current_lock.decode())
            if int(lock_params['id']) == self._id:
                # print('Lock is mine %s' % json.dumps(lock_params))
                return 'mine'
            elif lock_params['expire'] < time_check:
                # print('Lock has expired: %s' % json.dumps(lock_params))
                return None
            else:
                # print('Exchange is locked by another')
                raise Exception('Exchange %s is locked by another task.' % self.exchange_code)
        else:
            return None

    def lock(self):
        lock_state = self._check_lock()
        if lock_state is None:
            d = datetime.datetime.now() + datetime.timedelta(0, 30)
            _lock = {'id': self._id, 'expire': d.timestamp()}
            self.redis_client.set('lock_%s' % self.exchange_code, json.dumps(_lock))

    def release(self):
        lock_state = self._check_lock()
        if lock_state == 'mine':
            self.redis_client.delete('lock_%s' % self.exchange_code)
        
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

    def get_trend(self, symbol, freq='1d', since=None, latest=True, wait=True):
        self._check_lock()
        last_timestamp = 0
        
        if latest:
            last_saved = self.ts_client.get_last(self.exchange_code, symbol, 'trend_data', extra_filters={'freq': freq})

            if len(last_saved.index) > 0:
                last_timestamp = int(last_saved['last_timestamp'])

        ohlcv = []
        if wait:
            time.sleep(self.exchange.rateLimit / 1000)
        ohlcv = self.exchange.fetch_ohlcv(symbol, freq, since=last_timestamp)
        
        if len(ohlcv) == 0:
            logger.debug('Fetched no trend data.')
            return self

        data_frame = DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        data_frame[['open', 'high', 'low', 'close', 'volume']] = data_frame[['open', 'high', 'low', 'close', 'volume']].astype('float64')
        data_frame['pd_timestamp'] = (data_frame['timestamp'] / 1000).apply(datetime.datetime.fromtimestamp)
        data_frame['symbol'] = symbol
        data_frame['freq'] = freq
        data_frame = data_frame.set_index('pd_timestamp')

        self.result['trend_data'] = data_frame
        logger.debug('Fetched %s trend: %s, %s.' % (len(data_frame.index), self.exchange_code, symbol))
        return self

    def get_trades(self, symbol, since=None, latest=True, wait=True):
        # import ipdb; ipdb.set_trace()
        self._check_lock()
        last_timestamp = 0
        
        if latest:
            last_saved = self.ts_client.get_last(self.exchange_code, symbol, 'trade_data')

            if len(last_saved.index) > 0:
                last_timestamp = int(last_saved['last_timestamp'])

        trades = []
        if wait:
            time.sleep(self.exchange.rateLimit / 1000)
        trades = self.exchange.fetch_trades(symbol, since=last_timestamp)
        
        if len(trades) == 0:
            logger.debug('Fetched no trade data.')
            return self

        data_frame = DataFrame(trades, columns=trades[0].keys())
        data_frame[['price', 'amount']] = data_frame[['price', 'amount']].astype('float64')
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
            try:
                self.ts_client.write_dataframe(
                    result_data[_fields[result_name] + _tags[result_name]],
                    result_name,
                    tags={
                        'exchange': self.exchange_code
                    },
                    tag_columns=_tags[result_name]
                )
            except Exception as e:
                logger.info(e)

        self.result.clear()
        return self



