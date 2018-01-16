import time

from celery import Celery
from celery.utils.log import get_task_logger

from vegamite.data import MarketData, TimeSeriesClient, redis_client, Database
from vegamite.model import Market
from vegamite.config import config

ts_client = TimeSeriesClient()
r = redis_client()
database = Database()

celery = Celery(__name__, broker=config.celery.broker_url)
logger = get_task_logger(__name__)


def make_celery(app):
    
    celery.conf.update(app.config)

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
    

celery.conf.beat_schedule = {
    'test_run_2_seconds': {
        'task': 'vegamite.tasks.poll_market_data',
        'schedule': 10.0
    }
}


@celery.task()
def poll_market_data():
    # Read data from redis, fallback to database if empty
    # TODO: Really want a DB connection pool here
    session = database.get_session()
    rows = session.query(Market).filter(Market.track_data=='T')
    exchanges = {}
    for row in rows:
        exchange = row.exchange_code.lower()
        symbol = row.symbol
        if exchanges.get(exchange) is None:
            exchanges[exchange] = [symbol]
        else:
            exchanges[exchange].append(symbol)
    
    for exchange in exchanges.keys():
        symbols = exchanges.get(exchange)
        
        exchange_lock = r.get('lock_%s' % exchange) == b'true'

        if not exchange_lock:
            get_exchange_data.delay(exchange, symbols)
        else:
            logger.info('Exchange %s is locked.' % exchange)
    session.close()
    

@celery.task()
def cache_markets():
    # Read markets from DB
    # Read markets from redis
    # If there is a difference - update redis
    pass


@celery.task()
def get_exchange_data(exchange, symbol):
    market_data = MarketData(exchange)

    if isinstance(symbol, str):
            symbol = [symbol]
        
    for s in symbol:
        # Context manager will lock the exchange for a time to prevent excess calls
        with market_data as m:
            market_data.save_latest_trades(s)


@celery.task()
def query_gdax_ohlcv():
    ohlcv_data = exchange.get_trend('BTC/USD', '1m')
    logger.info('Collected gdax %s rows of ohlcv data' % len(ohlcv_data.index))
    
    ts_client.write_dataframe(
        ohlcv_data,
        'test_data', 
        tags={
            'exchange': 'gdax',
            'symbol': 'BTC/USD',
            'resolution': '1m'
        }, 
        field_columns=['open', 'high', 'low', 'close', 'volume'],
    )
    logger.info('Wrote %s rows to Influxdb' % len(ohlcv_data.index))


# celery.conf.beat_schedule = {
#     'query-every-10-seconds': {
#         'task': 'vegamite.vegamite.query_gdax_ohlcv',
#         'schedule': 10.0
#     }
# }

# @celery.task()



# @celery.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     # TODO: Read database to get list of markets I want to track, and set them up
#     sender.add_periodic_task(3.0, get_trades.s('gdax', 'BTC/USD'), name='gdax-BTC/USD')


# THIS MIGHT BE USEFUL
# @worker_ready.connect
# def start_polling(sender, **kwargs):
#     #pass
#     with sender.app.connection() as conn:
#         sender.app.send_task('vegamite.vegamite.poll_trades', connection=conn)

