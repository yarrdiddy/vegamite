
from numpy import log, exp
from numpy.random import randn

from vegamite.data import TimeSeriesClient, MarketData


class Analytic(object):
    """
    Analytics class - for now. Probably break it up.
    """
    def __init__(self):
        pass

    def get_points(self, exchange, symbol, freq):
        pass


class PriceSimulation(object):
    """
    Simulate price. Geometric brownian motion for now, probably introduce more sims later and generalize bits.

    Methods: 
        - Gather data, either on init or explicit... explicitly
        - Configure simulation
        - Run simulation
        - Save
    """

    def __init__(self, exchange, symbol, freq):

        self.exchange = exchange
        self.symbol = symbol
        self.freq = freq

        self._data = None
        self._result = None

        self.market_data = MarketData(exchange)
        self.ts_client = TimeSeriesClient()

    @property
    def data(self, data):
        self._data = data
        return self._data

    @data.setter
    def data(self):
        pass

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self):
        pass

    def configure(self):
        return self

    def fetch(self):
        query_params = dict(
            exchange=self.exchange
            symbol=self.symbol
            freq=self.freq
        )
        query_data = self.ts_client.query(
            """
            select  *
            from    trend_data
            where   exchange = %(exchange)s
            and     symbol = %(symbol)s
            and     freq = %(freq)s
            """ % query_params
        )
        self.data = query_data.get('trend_data')
        return self

    def run(self):
        data = self.data

        data['return'] = log(data['close']

        return self

    def save(self):
        return self