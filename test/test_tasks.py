import pytest

from vegamite.tasks import poll_exchanges

#TODO: Mock all the celery bits
def test_poll_exchanges():
    poll_exchanges()

# def test_poll_new_trades():
#     poll_new_trades('trade_data')
#     get_exchange_data('gdax')
