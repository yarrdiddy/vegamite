import time, json

from celery import Celery
from celery.schedules import crontab
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
    'queue_tasks_trades': {
        'task': 'vegamite.tasks.queue_tasks',
        'schedule': 30.0,
        'args': ['trade_data']
    },
    # 'queue_tasks_trends': {
    #     'task': 'vegamite.tasks.queue_tasks',
    #     'schedule': 60.0,
    #     'args': ['trend_data'],
    #     'kwargs': {'freq': '5m'}
    # },
    'run_market_data_tasks':{
        'task': 'vegamite.tasks.poll_exchanges',
        'schedule': 10.0,
    },
    'poll_5m_trend': {
        'task': 'vegamite.tasks.queue_tasks',
        'schedule': crontab(minute=0, hour='*'),
        'args': ['trend_data', '5m']
    },
    'poll_1h_trend': {
        'task': 'vegamite.tasks.queue_tasks',
        'schedule': crontab(minute=0, hour=0, day_of_week='*'),
        'args': ['trend_data', '1h']
    },
    'poll_1d_trend': {
        'task': 'vegamite.tasks.queue_tasks',
        'schedule': crontab(minute=15, hour=0, day_of_week='*'),
        'args': ['trend_data', '1d']
    }
}


@celery.task()
def queue_tasks(data_type, **kwargs):
    # Read data from redis, fallback to database if empty
    
    session = database.get_session()
    rows = session.query(Market).filter(Market.track_data=='T')
    exchanges = []

    new_tasks = []
    exchanges = r.lrange('poll-exchanges', 0, -1) or []
    
    # Get the markets that we need to poll in this run
    for row in rows:
        exchange = row.exchange_code.lower()
        symbol = row.symbol

        if exchange not in exchanges:
            exchanges.append(exchange)

        _task = dict(
            task=data_type,
            symbol=symbol,
            **kwargs
        )

        _task = json.dumps(_task)

        # Pending tasks will be added to a queue in redis
        # This is deliberately kept outside of celery in order to dynamically allocate asynchronous execution on each exchange.
        # tl;dr this will prevent excess calls on any one exchange.
        # pending_tasks = r.lrange('%s-tasks' % exchange, 0, -1)
        # pending_tasks = [json.loads(i.decode()) for i in pending_tasks]
    
        # if _task not in pending_tasks:
        #     r.lpush('%s-tasks' % exchange, _task)
        r.sadd('%s-tasks' % exchange, _task)

    for exchange in exchanges:
        r.sadd('exchange-queue', exchange)
    # print(r.smembers('exchange-queue'))
    session.close()



@celery.task()
def poll_exchanges():
    # session = database.get_session()
    # rows = session.query(Market.exchange_code).filter(Market.track_data=='T').distinct()

    while True:
        _exchange = r.spop('exchange-queue')
        if _exchange is None:
            break
        get_exchange_data.delay(_exchange.decode())
    

@celery.task()
def get_exchange_data(exchange):
    # import ipdb; ipdb.set_trace()
    market_data = MarketData(exchange)

    while True:
        _task = r.spop('%s-tasks' % exchange)
        if _task is None: 
            break

        logger.info('Performing task: %s' % _task)

        _task = json.loads(_task.decode())
        data_type = _task.get('task')
        symbol = _task.get('symbol')
        freq = _task.get('freq')

        with market_data as m:
            try:
                # print(r.lrange('%s-tasks' % exchange, 0, -1))
                # print(r.smembers('%s-tasks' % exchange))
                if data_type == 'trade_data':
                    m.get_trades(symbol).save()
                elif data_type == 'trend_data':
                    m.get_trend(symbol, freq=freq).save()

            except Exception as e:
                continue



@celery.task()
def query_gdax_ohlcv():
    ohlcv_data = exchange.get_trend('BTC/USD', '1m')
    logger.debug('Collected gdax %s rows of ohlcv data' % len(ohlcv_data.index))
    
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
    logger.debug('Wrote %s rows to Influxdb' % len(ohlcv_data.index))


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

