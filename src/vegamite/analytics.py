
from numpy import log, exp, mean, std, sqrt
from numpy.random import randn

from vegamite.data import TimeSeriesClient, MarketData
from vegamite.base import BaseAnalytic


class Analytic(BaseAnalytic):
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

    RUNTIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, exchange, symbol, freq):

        self.exchange = exchange
        self.symbol = symbol
        self.freq = freq

        self.method = 'geometric_brownian_motion'

        self._data = None
        self._result = None

        self.run_count = 0
        self.run_time = None

        self.market_data = MarketData(exchange)
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

    def configure(self):
        return self

    def fetch(self):
        # TODO: fetch should have a from argument
        query_params = dict(
            exchange=self.exchange,
            symbol=self.symbol,
            freq=self.freq,
        )
        query_data = self.ts_client.client.query(
            """
            select  *
            from    trend_data
            where   exchange = '%(exchange)s'
            and     symbol = '%(symbol)s'
            and     freq = '%(freq)s'
            """ % query_params
        )
        self.data = query_data.get('trend_data')
        return self

    def run(self):
        # Copy data to work on
        _data = self.data.copy()

        # Log returns
        _data['return'] = log(data['close'] / _data['open'])

        # Return stats for data set
        daily_volatility = std(_data['return'])
        annual_volatility = daily_volatility * sqrt(365)
        daily_drift = mean(_data['return'])
        annual_drift = daily_drift * 365
        mean_drift = daily_drift - 0.5 * daily_volatility**2

        # Random sample for the simulation
        _data['random_number'] = randn(len(_data.index))

        # The base ruturn multiplier, will be applied recursively to each simulated price
        _data['log_return'] = mean_drift + daily_volatility * _data['random_number']

        # Generate the random walk, starting from first close
        last_price = None
        first = True
        _simulated_price = []
        for i in _data.itertuples():
            if first:
                last_price = i.close
                _simulated_price.append(last_price)
                first = False
                continue
            
            new_price = last_price * exp(i.log_return)
            
            _simulated_price.append(new_price)
            last_price = new_price

        # Set some tag data
        _data['price'] = _simulated_price
        _data['run_count'] = self.run_count

        # Move results into result value
        self.result = _data[['price', 'exchange', 'symbol', 'freq', 'run_count']]

        # If the instance has never run before, set the run time
        if self.run_time is None:
            self.run_time = datetime.datetime.now()

        return self

    def save(self):
        # Save the simulation run with its metadata
        ts_client.write_dataframe(
            self.result,
            'simulation_result',
            tags={
                'run_time': self.run_time.strftime(PriceSimulation.RUNTIME_FORMAT), 
                'method': self.method
            },
            field_columns=['price'],
            tag_columns=['exchange', 'symbol', 'freq', 'run_count']
        )

        # Increment the run count here because we only care about saved runs
        self.run_count += 1
        return self



