import pytest

from vegamite.analytics.simulation import PriceSimulation
from vegamite.analytics.averages import EWMA

import ipdb

def test_simulation_run():
	# ipdb.set_trace()
	sim = PriceSimulation('gdax', 'BTC/USD', '5m', time_range='7 days')

	sim = sim.fetch()
	# sim = sim.run()
	
	for i in range(10):
		sim = sim.run().save()


def test_ewma():
	ewma = EWMA('gdax', 'BTC/USD', '5m', time_range='90 days')

	ewma  = ewma.fetch()
	ewma = ewma.run()
	# ewma = ewma.save()

