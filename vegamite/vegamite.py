import time

from flask import Flask, request, jsonify
from celery.utils.log import get_task_logger
from celery.signals import worker_ready
from numpy import int64

from vegamite.tasks import make_celery
from vegamite.data import MarketData, TimeSeriesClient

app = Flask(__name__)
logger = get_task_logger(__name__)

ts_client = TimeSeriesClient()
exchange = MarketData(exchange_code='gdax')


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


@celery.task()
def get_trades(exchange, symbol, track_since=None):
    """
    Given and exchange, poll the market data for the given symbol and save it in InfluxDB.
    """
    market_data = MarketData(exchange)

    last_saved_trade = ts_client.get_last_trade(exchange, symbol)
    last_timestamp = 0
    
    if len(last_saved_trade.index) > 0:
        last_timestamp = int(last_saved_trade['last'])

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


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # TODO: Read database to get list of markets I want to track, and set them up
    sender.add_periodic_task(3.0, get_trades.s('gdax', 'BTC/USD'), name='gdax-BTC/USD')


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



