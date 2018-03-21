import pytest

from vegamite.tasks import poll_exchanges, run_simulations, run_single_simulation

#TODO: Mock all the celery bits
def test_poll_exchanges():
    poll_exchanges()


def test_sim_task():
	run_simulations()
	run_single_simulation('gdax', 'BTC/USD', 10)

# def test_poll_new_trades():
#     poll_new_trades('trade_data')
#     get_exchange_data('gdax')

def test_trades():
	pass