from flask import Flask, request, jsonify
from celery.utils.log import get_task_logger


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

celery.conf.beat_schedule = {
    'query-every-10-seconds': {
        'task': 'vegamite.vegamite.query_gdax_ohlcv',
        'schedule': 10.0
    }
}


@celery.task()
def add_together(x, y):
    return x + y


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


# @celery.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(10.0, test.s('Hello'), name='add every 10 seconds')

#     sender.add_periodic_task(30.0, test.s('World!'), name='add every 30 seconds', expires=10)


# @celery.task()
# def test(arg):
#     print(arg)



@app.route("/")
def hello():
    return 'Hello World'


if __name__ == '__main__':
    app.run(debug=True)