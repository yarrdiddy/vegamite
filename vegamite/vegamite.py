import time
import redis

from flask import Flask, request, jsonify
from celery.utils.log import get_task_logger
from celery.signals import worker_ready
from numpy import int64

from vegamite.tasks import make_celery
from vegamite.data import MarketData, TimeSeriesClient, redis_client, get_database_connection
from vegamite.model import Market

app = Flask(__name__)
logger = get_task_logger(__name__)

ts_client = TimeSeriesClient()
exchange = MarketData(exchange_code='gdax')
r = redis_client()

app.config.update(
    CELERY_BROKER_URL='pyamqp://guest@localhost',
    result_backend='rpc://guest@localhost'
)

celery = make_celery(app)

# celery.conf.beat_schedule = {
#     'query-every-10-seconds': {
#         'task': 'vegamite.vegamite.query_gdax_ohlcv',
#         'schedule': 10.0
#     }
# }

celery.conf.beat_schedule = {
    'test_run_2_seconds': {
        'task': 'vegamite.vegamite.schedule_data_polling',
        'schedule': 10.0
    }
}

@celery.task()
def dummy_task(*args):
    """Literally do nothing..."""
    return args


@celery.task()
def schedule_data_polling():
    # Read data from redis, fallback to database if empty
    # TODO: Really want a DB connection pool here
    session = get_database_connection()
    rows = session.query(Market).filter(Market.track_data=='T')
    task_chain = []
    for row in rows:
        exchange = row.exchange_code.lower()
        symbol = row.symbol

        exchange_lock = r.get('lock_%s' % exchange) == b'true'

        if not exchange_lock:
            get_trades(exchange, symbol)
        else:
            logger.info('Exchange %s is locked.' % exchange)
    session.close()
    # logger.info(task_chain)
    # dummy_task.apply_async(link=task_chain)


@celery.task()
def cache_markets():
    # Read markets from DB
    # Read markets from redis
    # If there is a difference - update redis
    pass


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


# @celery.task()
def get_trades(exchange, symbol, track_since=None):
    """
    Given and exchange, poll the market data for the given symbol and save it in InfluxDB.
    """
    logger.info('Exchange name is: %s' % exchange)
    market_data = MarketData(exchange)

    last_saved_trade = ts_client.get_last_trade(exchange, symbol)
    last_timestamp = 0
    
    if len(last_saved_trade.index) > 0:
        last_timestamp = int(last_saved_trade['last'])

    # Lock the exchange
    r.set('lock_%s' % exchange, 'true')
    trades = market_data.get_trades(symbol, since=last_timestamp)
    
    if len(trades.index) == 0:
        logger.info('No new trades for %s, timestamp = %s' % (symbol, last_timestamp))
    else:
        ts_client.write_dataframe(
            trades[['symbol', 'side', 'id', 'price', 'amount', 'timestamp']],
            'test_trade_data',
            tags={
                'exchange': exchange
            },
            tag_columns=['symbol', 'side']
        )
        logger.info('Wrote %s trades for %s, timestamp = %s' % (len(trades.index), symbol, last_timestamp))
    
    time.sleep(market_data.exchange.rateLimit / 1000)
    r.set('lock_%s' % exchange, 'false')


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


@app.route("/")
def hello():
    return 'Hello World'


if __name__ == '__main__':
    app.run(debug=True)



