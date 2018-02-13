import datetime

from abc import ABCMeta, abstractmethod
from celery.utils.log import get_task_logger

from vegamite.data import TimeSeriesClient
from vegamite.utils.timeutil import parse_time_range

logger = get_task_logger(__name__)

class Analytic(metaclass=ABCMeta):
    """
    Analytics class - for now. Probably break it up.
    """

    RUNTIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self):
        self._data = None
        self._result = None
        self.run_time = None
        self.ts_client = TimeSeriesClient()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, result):
        self._result = result

    def _set_time_range(self, **kwargs):
        start_time = kwargs.get('start_time')
        end_time = kwargs.get('end_time')
        time_range = kwargs.get('time_range')

        if end_time is None:
            end_time = datetime.datetime.utcnow()
        else:
            end_time = datetime.strftime(end_time)

        if start_time:
            start_time = datetime.strftime(start_time)
        elif time_range:
            try:
                offset = parse_time_range(time_range)

            except Exception as e:
                logger.info('Could not parse time_range, defaulting to 1 month')
                offset = datetime.timedelta(days=30)

            start_time = end_time - offset
        else:
            start_time = end_time

        self.start_time = start_time.timestamp()
        self.end_time = end_time.timestamp()

    @abstractmethod
    def configure(self, *args, **kwargs):
        pass

    @abstractmethod
    def fetch(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def save(self):
        pass


class TrendAnalytic(Analytic):

    def fetch(self):
        if self.end_time is None:
            end_time = int(datetime.datetime.utcnow().timestamp() * 1e9)
        else:
            end_time = int(self.end_time * 1e9)

        if self.start_time != 0:
            start_time = int(self.start_time * 1e9)

        query_params = dict(
            exchange=self.exchange,
            symbol=self.symbol,
            freq=self.freq,
            start_time=self.start_time,
            end_time=end_time,
        )
        query_data = self.ts_client.client.query(
            """
            select  *
            from    trend_data
            where   exchange = '%(exchange)s'
            and     symbol = '%(symbol)s'
            and     freq = '%(freq)s'
            and     time <= %(end_time)s
            and     time >= %(start_time)s 
            """ % query_params
        )
        self.data = query_data.get('trend_data')
        return self 
