import time, json

from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from kombu import Queue

from vegamite.data import MarketData, TimeSeriesClient, redis_client, Database
from vegamite.model import Market
from vegamite.config import config
from vegamite.analytics.simulation import PriceSimulation

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
    
# celery.conf.task_queues = (
#     Queue('data'),
#     Queue('analytics'),
# )

# celery.control.add_consumer('data', reply=True)
# celery.control.add_consumer('analytics', reply=True)

celery.conf.beat_schedule = {
    'queue_tasks_trades': {
        'task': 'vegamite.tasks.queue_tasks',
        'schedule': 30.0,
        'args': ['trade_data']
    },
    'run_market_data_tasks':{
        'task': 'vegamite.tasks.poll_exchanges',
        'schedule': 10.0,
    },
    # 'poll_5m_trend': {
    #     'task': 'vegamite.tasks.queue_tasks',
    #     'schedule': crontab(minute='*/15', hour='*'),
    #     'args': ['trend_data'],
    #     'kwargs': {'freq': '5m'}
    # },
    # 'poll_1h_trend': {
    #     'task': 'vegamite.tasks.queue_tasks',
    #     'schedule': crontab(minute='0', hour='*/3', day_of_week='*'),
    #     'args': ['trend_data'],
    #     'kwargs': {'freq': '1h'}
    # },
    # 'poll_1d_trend': {
    #     'task': 'vegamite.tasks.queue_tasks',
    #     'schedule': crontab(minute='15', hour='0', day_of_week='*'),
    #     'args': ['trend_data'],
    #     'kwargs': {'freq': '1d'}
    # },
    # 'run_simulations': {
    #     'task': 'vegamite.tasks.run_simulations',
    #     'schedule': crontab(minute='30', hour='*')
    # }
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

        logger.info('Found: %s, %s' % (exchange, symbol))

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
        r.sadd('%s-tasks' % exchange, _task)

    for exchange in exchanges:
        r.sadd('exchange-queue', exchange)
    session.close()



@celery.task()
def poll_exchanges():
    while True:
        _exchange = r.spop('exchange-queue')
        if _exchange is None:
            break
        get_exchange_data.delay(_exchange.decode())
    

@celery.task()
def get_exchange_data(exchange):
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
                if data_type == 'trade_data':
                    m.get_trades(symbol).save(retention_policy="test_policy")
                elif data_type == 'trend_data':
                    if m.exchange_code == 'gdax':
                        m = m.get_trend(symbol, freq=freq, latest=False)
                    else:
                        m = m.get_trend(symbol, freq=freq)
                    if not m.result.get('trend_data'):
                        r.sadd('%s-tasks' % exchange, json.dumps(_task))
                    m.save()

            except Exception as e:
                continue

@celery.task()
def run_simulations():
    # import ipdb; ipdb.set_trace()
    session = database.get_session()
    rows = session.query(Market).filter(Market.backtest_market=='T')
    
    for row in rows:
        exchange = row.exchange_code.lower()
        symbol = row.symbol
        logger.debug('Running simulation: %s, %s' % (exchange, symbol))
        run_single_simulation.delay(exchange, symbol, 1000)

    session.close()


@celery.task()
def run_single_simulation(exchange, symbol, iterations):
    simulation = PriceSimulation(exchange, symbol, '5m', time_range='7 days')
    simulation = simulation.fetch()

    for i in range(iterations):
        simulation = simulation.run().save()




