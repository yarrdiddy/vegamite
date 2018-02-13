import datetime

from pandas import ewma

from vegamite.data import TimeSeriesClient, MarketData
from vegamite.analytics.base import TrendAnalytic
from vegamite.utils.timeutil import parse_time_range


class EWMA(TrendAnalytic):
    """
    Exponentially weighted moving average
    """
    def __init__(self, exchange, symbol, freq, **kwargs):

        self.exchange = exchange
        self.symbol = symbol
        self.freq = freq

        self.start_time = 0
        self.end_time = None
        self.run_count = 0

        self.center_of_mass = None
        self.span = None
        self.alpha = None

        self.market_data = MarketData(exchange)

        self.configure(**kwargs)

        super().__init__()

    def configure(self, **kwargs):
        """
        Configure the average.
        """
        self._set_time_range(**kwargs)

        self.center_of_mass = kwargs.get('center_of_mass')
        self.span = kwargs.get('span')
        self.alpha = kwargs.get('alpha')
        
        return self

    def run(self):
        import ipdb; ipdb.set_trace()
        if self.data is None:
            return self
        # Copy data to work on
        _data = self.data.copy()

        # Only going to use span for now...
        _data['avg_close'] = ewma(_data, span=self.span)

        self.result = _data[['exchange', 'symbol', 'freq', 'avg_close']]
        
        return self

    def save(self):
        if self.result is None:
            return self

        # Save the simulation run with its metadata
        self.ts_client.write_dataframe(
            self.result,
            'average_data',
            tags={
                'run_time': self.run_time.strftime(PriceSimulation.RUNTIME_FORMAT), 
                'method': 'ewma',
                
            },
            field_columns=['price'],
            tag_columns=['exchange', 'symbol', 'freq', 'run_count']
        )
        return self        





