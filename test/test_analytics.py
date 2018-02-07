import pytest

from vegamite.analytics import PriceSimulation

def test_simulation_run():
	sim = PriceSimulation('gdax', 'BTC/USD', '5m')

	sim = sim.fetch()
	# sim = sim.run()
	import ipdb; ipdb.set_trace()
	for i in range(1000):
		sim = sim.run().save()